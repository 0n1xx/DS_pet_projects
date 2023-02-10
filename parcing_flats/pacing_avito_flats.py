import pandas as pd
import requests
from hyper.contrib import HTTP20Adapter
from bs4 import BeautifulSoup as bs
from time import sleep
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.models import Variable
from datetime import datetime, timedelta
from clickhouse_driver import Client
import emoji  # Для особой миссии !
import telegram

# Параметры для airflow
default_args = {
    'owner': Variable.get("AIRFLOW_OWNER"),  # airflow
    'depends_on_past': False,
    'email': list(Variable.get("MAIL_TO_REPORT")),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'start_date': datetime(2022, 9, 3),
}
schedule_interval = "00 22 * * 4"

client = Client(host=Variable.get("CLICKHOUSE_HOST"))
my_token = Variable.get("TG_TOKEN_AVITO")
bot = telegram.Bot(token=my_token)
chat_id = Variable.get("CHAT_ID_MOSCOW_FLATS")

dag = DAG('parcing_flats', default_args=default_args, schedule_interval=schedule_interval, catchup=False)

def parce_flats(ti):
    lst_links, lst_square, lst_price, lst_subway, lst_description, lst_minutes = [], [], [], [], [], []

    for page in range(1, 99):
        print(emoji.emojize(f'Идет {page} страница :monkey:'))
        full_url = f"https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1&p={page}"
        source = requests.Session()
        source.mount('https://', HTTP20Adapter())  # адаптер, чтобы сервер не воспринимал нас как бота
        response = source.get(full_url)
        sleep(7)
        response.encoding = 'utf-8'
        soup = bs(response.text, 'lxml')

        all_flats = soup.findAll("div", class_="iva-item-content-rejJg")

        for flat in all_flats:

            # Ссылка на квартиру:
            var_link = flat.find("a",
                                 "link-link-MbQDP link-design-default-_nSbv title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH")
            if var_link is not None:
                local_var_link = "https://www.avito.ru" + var_link.get("href")
                lst_links.append([local_var_link])
            else:
                lst_links.append([None])

            # Цена на квадратный метр:
            var_square = flat.find("span",
                                   class_="price-noaccent-X6dOy price-normalizedPrice-PplY9 text-text-LurtD text-size-s-BxGpL")
            if var_square is not None:
                var = flat.find("span",
                                class_="price-noaccent-X6dOy price-normalizedPrice-PplY9 text-text-LurtD text-size-s-BxGpL").text
                correct_number_square_price = ""
                for var_square_circle in var:
                    if var_square_circle.isdigit():
                        correct_number_square_price += var_square_circle
                # Убираем последнею цифру так как там значение в квадрате:
                correct_number_square_price = correct_number_square_price.replace(correct_number_square_price[-1],
                                                                                  "")
                lst_square.append(correct_number_square_price)
            else:
                lst_square.append(None)

            # Полное число
            var_full_price = flat.find("span", class_="price-text-_YGDY text-text-LurtD text-size-s-BxGpL")
            if var_full_price is not None:
                full_price = var_full_price.text
                correct_number_full_price = ""
                # Оставляем лишь число:
                for var_full_price_circle in full_price:
                    if var_full_price_circle.isdigit():
                        correct_number_full_price += var_full_price_circle
                lst_price.append(correct_number_full_price)
            else:
                lst_price.append(None)

            # Станция метро
            var_subway = flat.find('div', class_="geo-georeferences-SEtee text-text-LurtD text-size-s-BxGpL")
            if var_subway is not None:
                subway_name = var_subway.text
                subway_full = ""
                for var_subway_circle in subway_name:
                    if var_subway_circle.isalpha() or var_subway_circle == " " or var_subway_circle == "-":
                        subway_full += var_subway_circle
                    else:
                        break
                # Прописываю if для тех случаев когда в название метро попадает от и до:
                if (subway_full[-1] == "т" and subway_full[-2] == "о") or (
                        subway_full[-1] == "о" and subway_full[-2] == "д"):
                    subway_full = subway_full[0:-2]
                lst_subway.append(subway_full)
            else:
                lst_subway.append(None)

            # Расстояние до метро:
            var_minutes = flat.find("span", class_="geo-periodSection-bQIE4")
            if var_minutes is not None:
                var_minutes_text = var_minutes.text
                var_minutes_full = ""
                for var_minute_circle in var_minutes_text:
                    if var_minute_circle == '–' or var_minute_circle.isdigit():
                        var_minutes_full += var_minute_circle
                lst_minutes.append(var_minutes_full)
            else:
                lst_minutes.append(None)

    full_df = pd.DataFrame(
        data={"square_price": lst_square, "full_price": lst_price, "subway": lst_subway, "links": lst_links,
              'destination_from_nearest_subway': lst_minutes})
    full_df.to_csv("parsed_data.csv", index=False)
    ti.xcom_push(key="parce_flats_df", value="parsed_data.csv")


def filter_df(ti):
    df = pd.read_csv(ti.xcom_pull(key='parce_flats_df', task_ids="parce_flats"))

    df = df.drop_duplicates(
        subset="links")  # порой попадаются дубликаты так как сайт 'динамически' переходит на следующею страницу
    df = df.dropna()
    df[["square_price", "full_price"]] = df[["square_price", "full_price"]].astype("int64")
    df[["subway", "links", "destination_from_nearest_subway"]] = df[
        ["subway", "links", "destination_from_nearest_subway"]].astype(str)
    df.links = df.links.str.replace("[", "")
    df.links = df.links.str.replace("]", "")
    df.links = df.links.str.replace("'", "")

    df["quantity_of_metres"] = (df["full_price"] / df["square_price"]).round()
    df["date_of_parsing"] = datetime.today().strftime('%Y-%m-%d')
    df["date_of_parsing"] = pd.to_datetime(df["date_of_parsing"])
    df.to_csv("filter_df.csv", index=False)
    ti.xcom_push(key="filter_parsed_data", value="filter_df.csv")

def uncommon_values(ti):

    df_new = pd.read_csv(ti.xcom_pull(key="filter_parsed_data", task_ids="filter_df"))

    # Достаем все записи из таблицы и создаем новый датафрейм:
    df_old = client.execute("Select * from avito_flats")
    df_old = pd.DataFrame(
        columns=["square_price", "full_price", "subway", "links", "destination_from_nearest_subway",
                 "quantity_of_metres", "date_of_parsing"],
        data=df_old)
    df_new_values = df_new.merge(df_old, on="links", how="left", indicator=True).loc[
        lambda x: x["_merge"] == 'left_only']
    df_new_values = df_new_values.drop(
        ["square_price_y", "full_price_y", "subway_y", "destination_from_nearest_subway_y", "quantity_of_metres_y",
         "date_of_parsing_y", "_merge"], axis=1)
    df_new_values = df_new_values.rename(
        columns={"square_price_x": "square_price", "full_price_x": "full_price", "subway_x": "subway",
                 "destination_from_nearest_subway_x": "destination_from_nearest_subway",
                 "quantity_of_metres_x": "quantity_of_metres", "date_of_parsing_x": "date_of_parsing"})
    df_new_values.to_csv("new_values.csv", index=False)
    ti.xcom_push(key="uncommon_values_df", value="new_values.csv")


def to_clickhouse(ti):
    df = pd.read_csv(ti.xcom_pull(key="uncommon_values_df", task_ids="uncommon_values"))
    df["date_of_parsing"] = pd.to_datetime(df["date_of_parsing"])
    client.execute("INSERT INTO default.avito_flats VALUES", df.to_dict(orient="records"))
    client.execute('OPTIMIZE TABLE default.avito_flats DEDUPLICATE BY links')

def cheap_flats(ti):

    df = pd.read_csv(ti.xcom_pull(key="uncommon_values_df", task_ids="uncommon_values"))
    def q15(x):
        return x.quantile(0.15)

    # Создаю датафрейм по каждой станции с 10 персентилем по каждой метрике
    metro_10_percentile = df.groupby("subway", as_index=False).agg({"full_price": q15, "square_price": q15}).rename(
        columns={"full_price": "full_price_10_percentile",
                 "square_price": "square_price_10_percentile"}).sort_values(
        "square_price_10_percentile", ascending=False)

    needed_flats = df.query("destination_from_nearest_subway in ('5','6-10')")
    both_frames = needed_flats.merge(metro_10_percentile, how="left", on="subway")
    cheep_flats = both_frames.query(
        "square_price <= square_price_10_percentile and full_price <= full_price_10_percentile").drop_duplicates(
        subset="links")
    cheep_flats = cheep_flats[
        ["square_price", "full_price", "subway", "links", "destination_from_nearest_subway", "quantity_of_metres"]]
    cheep_flats.to_csv("cheep_flats.csv", index=False)
    ti.xcom_push("cheap_flats_df", value="cheep_flats.csv")

def send_cheap_flats(ti):
    df = pd.read_csv(ti.xcom_pull(key="cheap_flats_df",task_ids="cheap_flats"))
    for index, row in df.iterrows():
        sleep(7)
        current_row = f"На сайте появилась выгодная квартира:\n" \
                      f"- Цена за квадратный метр следующая {row[0]};\n" \
                      f"- Полная цена = {row[1]};\n" \
                      f"- Кол-во квадратных метров = {row[5]};\n" \
                      f"- Находиться на станции метро = {row[2]} ({row[4]} минуток от метро).\n" \
                      f"Если вас заинтересовало данное предложение переходите по ссылке: {row[3]}"
        bot.sendMessage(chat_id=chat_id, text=current_row)



parce_flats = PythonOperator(
    python_callable=parce_flats,
    dag=dag,
    task_id="parce_flats",
    do_xcom_push=False
)

filter_df = PythonOperator(
    python_callable=filter_df,
    dag=dag,
    task_id="filter_df",
    do_xcom_push=False
)

uncommon_values = PythonOperator(
    python_callable=uncommon_values,
    dag=dag,
    task_id="uncommon_values",
    do_xcom_push=False
)

to_clickhouse = PythonOperator(
    python_callable=to_clickhouse,
    dag=dag,
    task_id="to_clickhouse",
    do_xcom_push=False
)

cheap_flats = PythonOperator(
    python_callable=cheap_flats,
    dag=dag,
    task_id="cheap_flats",
    do_xcom_push=False
)

send_cheap_flats = PythonOperator(
    python_callable=send_cheap_flats,
    dag=dag,
    task_id="send_cheap_flats",
    do_xcom_push=False
)

parce_flats >> filter_df >> uncommon_values >> to_clickhouse
uncommon_values >> cheap_flats >> send_cheap_flats