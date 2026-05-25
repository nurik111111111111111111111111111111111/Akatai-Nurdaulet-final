### Зачем нужен CSV

CSV - это простая таблица в текстовом файле. Его можно открыть в Excel, Google Sheets или прочитать через Python.

`Query` нужен, чтобы принимать параметры из адресной строки.

```python
from fastapi.responses import FileResponse
```

Подключает `FileResponse`.

Он нужен, чтобы API мог вернуть файл, например PNG-картинку с графиком.

## 3. Настройка matplotlib

Код:

```python
plt.switch_backend("Agg")
```

### Что делает строка

Эта строка говорит `matplotlib`: не открывай отдельное окно с графиком, просто сохрани график в файл.

### Зачем это нужно

На сервере или в API обычно нет смысла открывать окно с картинкой. Нам нужно только создать файл:

```text
internship_salaries.png
```

Без этой строки matplotlib может попытаться открыть окно через Tkinter. На некоторых компьютерах из-за этого появляется ошибка `TclError`.

Аналогия: вместо того чтобы показывать рисунок на экране, программа сразу сохраняет его как фотографию.

## 9. Метод `generate_json_by_stack`

Код:

```python
def generate_json_by_stack(self, stack):
    vacancies = self.filter_by_stack(stack)
    result = {
        "направление": stack,
        "количество": len(vacancies),
        "вакансии": vacancies,
    }

    with open("internships_filtered.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    return result
```

### Объяснение каждой строки

```python
def generate_json_by_stack(self, stack):
```

Создается метод, который делает JSON по выбранному направлению.

```python
vacancies = self.filter_by_stack(stack)
```

Сначала метод вызывает фильтр.

Например, если `stack = "python"`, то метод получит только Python-вакансии.

```python
result = {
    "направление": stack,
    "количество": len(vacancies),
    "вакансии": vacancies,
}
```

Создается словарь с результатом.

`"направление": stack` показывает, какое направление выбрали.

`"количество": len(vacancies)` считает, сколько вакансий найдено.

`"вакансии": vacancies` хранит сам список вакансий.

```python
with open("internships_filtered.json", "w", encoding="utf-8") as file:
```

Открывается файл `internships_filtered.json` для записи.

`"w"` означает write, то есть запись.

`encoding="utf-8"` нужно, чтобы русские буквы сохранились нормально.

```python
json.dump(result, file, ensure_ascii=False, indent=2)
```

Сохраняет словарь `result` в JSON-файл.

`ensure_ascii=False` нужно, чтобы русские буквы не превратились в коды вроде `\u043a`.

`indent=2` делает файл красивым, с отступами.

## 10. Метод `groupby_stack`

Код:

```python
def groupby_stack(self):
    grouped = self.df.groupby("stack", as_index=False)["salary"].agg(
        количество="count",
        медианная_зарплата="median",
    )
    grouped = grouped.rename(columns={"stack": "направление"})
    return grouped.to_dict(orient="records")
```

### Объяснение каждой строки

```python
def groupby_stack(self):
```

Создается метод группировки по направлению.

```python
grouped = self.df.groupby("stack", as_index=False)["salary"].agg(...)
```

Здесь pandas группирует вакансии по столбцу `stack`.

То есть все `python` собираются в одну группу, все `java` в другую, все `qa` в третью.

Аналогия: как разложить карточки вакансий по папкам:

- папка `python`;
- папка `java`;
- папка `qa`;
- папка `frontend`;
- папка `data`.

```python
["salary"]
```

После группировки pandas работает только со столбцом зарплат.

```python
.agg(
    количество="count",
    медианная_зарплата="median",
)
```

`agg` означает aggregation, то есть вычисление итоговых значений.

`количество="count"` считает количество вакансий в каждой группе.

`медианная_зарплата="median"` считает медианную зарплату в каждой группе.

```python
grouped = grouped.rename(columns={"stack": "направление"})
```

Переименовывает столбец `stack` в `направление`.

Эта строка не обязательная для работы программы. Она нужна только для красивого и понятного ответа API.

Если строку оставить, ответ будет таким:

```json
[
  {
    "направление": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

Если строку удалить, программа все равно будет работать, но ответ будет таким:

```json
[
  {
    "stack": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

То есть меняется только название поля в результате: `stack` или `направление`.

## Отдельно: два важных метода для группировки и медианы

Ниже разобраны два места, которые часто сложнее всего понять:

1. Метод `groupby_stack`.
2. Строка `return {stack: int(salary) for stack, salary in medians.items()}` из метода `median_salaries`.

### 1. Метод `groupby_stack`

Код:

```python
def groupby_stack(self):
    grouped = self.df.groupby("stack", as_index=False)["salary"].agg(
        количество="count",
        медианная_зарплата="median",
    )
    grouped = grouped.rename(columns={"stack": "направление"})
    return grouped.to_dict(orient="records")
```

Что делает метод:

Он берет все вакансии из таблицы и группирует их по направлению `stack`.

Например, если в CSV есть:

```text
python
python
java
qa
python
```

то pandas собирает одинаковые направления вместе:

```text
python -> все Python-вакансии
java   -> все Java-вакансии
qa     -> все QA-вакансии
```

Строка:

```python
self.df.groupby("stack", as_index=False)
```

означает: сгруппировать таблицу по столбцу `stack`.

`as_index=False` нужен, чтобы `stack` остался обычным столбцом, а не стал индексом таблицы.

Строка:

```python
["salary"]
```

означает: после группировки работать только с зарплатами.

Строка:

```python
.agg(
    количество="count",
    медианная_зарплата="median",
)
```

говорит pandas посчитать два значения:

`количество="count"` - сколько вакансий в каждой группе.

`медианная_зарплата="median"` - медианную зарплату в каждой группе.

Пример:

```text
python salary: 180000, 210000, 220000, 250000
```

Медиана будет:

```text
(210000 + 220000) / 2 = 215000
```

В конце:

```python
return grouped.to_dict(orient="records")
```

превращает pandas-таблицу в список словарей, чтобы FastAPI мог вернуть это как JSON.

Пример результата:

```json
[
  {
    "направление": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

Зачем нужен метод:

Он нужен для endpoint `/vacancies/grouped`, чтобы показать статистику по каждому направлению.

### 2. Строка со словарем в `median_salaries`

Код метода:

```python
def median_salaries(self):
    medians = self.df.groupby("stack")["salary"].median().sort_values(ascending=False)
    return {stack: int(salary) for stack, salary in medians.items()}
```

Главная строка:

```python
return {stack: int(salary) for stack, salary in medians.items()}
```

Что делает метод:

Он считает медианную зарплату по каждому направлению и возвращает короткий словарь.

Сначала:

```python
medians = self.df.groupby("stack")["salary"].median().sort_values(ascending=False)
```

pandas получает примерно такой результат:

```text
data        225000.0
java        215000.0
python      215000.0
frontend    180000.0
qa          167500.0
```

Потом:

```python
medians.items()
```

проходит по каждой паре:

```text
направление + зарплата
```

Например:

```python
"python", 215000.0
```

Строка:

```python
{stack: int(salary) for stack, salary in medians.items()}
```

создает словарь.

То есть из такого результата pandas:

```text
python -> 215000.0
java   -> 215000.0
data   -> 225000.0
```

получается обычный словарь Python:

```python
{
    "python": 215000,
    "java": 215000,
    "data": 225000
}
```

`int(salary)` нужен, чтобы убрать `.0`.

Было:

```python
215000.0
```

Стало:

```python
215000
```

Зачем нужен метод:

Он нужен для построения графика. Графику нужны названия направлений и их медианные зарплаты:

```python
plt.bar(medians.keys(), medians.values(), color="green")
```

`medians.keys()` - это направления.

`medians.values()` - это зарплаты.

```python
return grouped.to_dict(orient="records")
```

Превращает итоговую таблицу в список словарей.

```python
return {stack: int(salary) for stack, salary in medians.items()}
```

Создает словарь.

Пример:

```python
{
    "data": 225000,
    "python": 215000,
    "qa": 167500
}
```

`int(salary)` делает число целым.

## 14. Метод `save_salary_chart`

```python
medians = self.median_salaries()
```

Получаем медианные зарплаты по направлениям.

```python
plt.figure(figsize=(9, 5))
```

Создаем новую область для графика.

`figsize=(9, 5)` означает размер графика.

```python
plt.bar(medians.keys(), medians.values(), color="green")
```

Создаем столбчатый график.

`medians.keys()` - названия направлений.

`medians.values()` - зарплаты.

## 15. Создание FastAPI-приложения

```python
@app.get("/vacancies")
```

Это декоратор FastAPI.

Он говорит: если пользователь отправит GET-запрос на `/vacancies`, запусти функцию ниже.

## 17. Endpoint `/vacancies/filter`

```python
@app.get("/vacancies/filter")
```

Создает GET endpoint `/vacancies/filter`.

```python
def vacancies_filter(stack: str = Query(...)):
```

Функция принимает параметр `stack`.

`stack: str` означает, что параметр должен быть строкой.

`Query(...)` означает, что параметр обязателен.

## 19. Endpoint `/vacancies/chart`
```

`path` хранит имя этого файла.

```python
return FileResponse(path, media_type="image/png")
```

FastAPI возвращает файл пользователю.

`media_type="image/png"` говорит браузеру: это PNG-картинка.

## 20. Как работает FileResponse

`FileResponse` нужен, когда API должен вернуть не JSON, а файл.

Обычный endpoint возвращает данные:

```python
return {"message": "hello"}
```

А `FileResponse` возвращает файл:

```python
return FileResponse("internship_salaries.png", media_type="image/png")
```

То есть FastAPI открывает файл на компьютере и отправляет его в браузер.

Браузер видит `media_type="image/png"` и понимает, что это картинка.

## 21. Запуск uvicorn

Код:

```python
if __name__ == "__main__":
    import uvicorn

    print("Docs: http://127.0.0.1:8010/docs")
    uvicorn.run(app, host="127.0.0.1", port=8010)
```

```python
import uvicorn
```

Подключает сервер `uvicorn`.

FastAPI сам по себе описывает API, но ему нужен сервер, который будет принимать запросы.

```python
print("Docs: http://127.0.0.1:8010/docs")
```

Печатает ссылку на документацию API.

```python
uvicorn.run(app, host="127.0.0.1", port=8010)
```

Запускает сервер.

`app` - FastAPI-приложение.

`host="127.0.0.1"` означает, что сервер работает только на твоем компьютере.

`port=8010` означает порт.

Итоговый адрес:

```text
http://127.0.0.1:8010
```

|---|---|
| `/vacancies` | Показывает все вакансии |
| `/vacancies/filter?stack=python` | Фильтрует вакансии по направлению и сохраняет JSON |
| `/vacancies/grouped` | Показывает количество вакансий и медианную зарплату по направлениям |
| `/vacancies/chart` | Создает и возвращает график зарплат |

## 25. Главное, что нужно понять

CSV - это исходные данные.

Pandas читает CSV и работает с таблицей.

`InternshipBoard` хранит методы для обработки вакансий.

FastAPI делает из методов API.

Uvicorn запускает сервер.

Matplotlib создает график.

FileResponse отправляет график как файл.

JSON нужен, чтобы сохранить результат фильтрации в отдельный файл.

## 26. Ответы на частые вопросы по коду

В этом разделе собраны короткие объяснения строк, про которые чаще всего возникают вопросы.

### Обязательно ли писать `indent=2`

Код:

```python
json.dump(result, file, ensure_ascii=False, indent=2)
```

`indent=2` не обязателен.

Он нужен только для красивого вида JSON-файла.

С `indent=2` файл будет выглядеть так:

```json
{
  "направление": "python",
  "количество": 4,
  "вакансии": []
}
```

Без `indent=2` файл будет в одну строку:

```json
{"направление":"python","количество":4,"вакансии":[]}
```

Оба варианта работают одинаково. Для учебного проекта лучше оставить `indent=2`, потому что преподавателю и студенту легче читать файл.

### Где посмотреть JSON-файл

JSON-файл создается этой частью кода:

```python
with open("internships_filtered.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=2)
```

Файл называется:

```text
internships_filtered.json
```

Он появляется в той же папке, где лежит Python-файл проекта.

Важно: файл появится только после запуска фильтра.

Например, нужно открыть:

```text
http://127.0.0.1:8010/vacancies/filter?stack=python
```

После этого в папке проекта появится:

```text
internships_filtered.json
```

### Обязательно ли писать `sort_values(ascending=False)`

Код:

```python
medians = self.df.groupby("stack")["salary"].median().sort_values(ascending=False)
```

`sort_values(ascending=False)` не обязателен.

Он сортирует значения от большего к меньшему.

С ним результат будет примерно такой:

```text
data        225000
java        215000
python      215000
frontend    180000
qa          167500
```

Если убрать:

```python
.sort_values(ascending=False)
```

код все равно будет работать:

```python
medians = self.df.groupby("stack")["salary"].median()
```

Просто порядок может быть обычным, чаще по алфавиту:

```text
data
frontend
java
python
qa
```

То есть сортировка нужна только для красивого порядка в ответе и на графике.

### Что значит `as_index=False`

Код:

```python
grouped = self.df.groupby("stack", as_index=False)["salary"].agg(
    количество="count",
    медианная_зарплата="median",
)
```

`as_index=False` нужен, чтобы `stack` остался обычным столбцом, а не стал индексом таблицы.

Пример исходной таблицы:

```text
company   stack   salary
Kaspi     python  180000
Yandex    python  220000
EPAM      java    200000
Sber      java    230000
```

Если написать без `as_index=False`:

```python
self.df.groupby("stack")["salary"].median()
```

результат будет примерно такой:

```text
stack
java      215000
python    200000
Name: salary
```

Здесь `stack` стал индексом. Индекс - это как название строки слева.

Если написать с `as_index=False`:

```python
self.df.groupby("stack", as_index=False)["salary"].median()
```

результат будет примерно такой:

```text
stack    salary
java     215000
python   200000
```

Здесь `stack` остался обычным столбцом.

В этом проекте так удобнее, потому что потом можно переименовать столбец:

```python
grouped = grouped.rename(columns={"stack": "направление"})
```

### Что значит `orient="records"`

Код:

```python
df.to_dict(orient="records")
```

`orient="records"` говорит pandas, в каком виде превратить таблицу в словари.

Есть таблица:

```text
company   stack   salary
Kaspi     python  180000
Yandex    python  220000
```

После:

```python
df.to_dict(orient="records")
```

получится список словарей:

```python
[
    {
        "company": "Kaspi",
        "stack": "python",
        "salary": 180000
    },
    {
        "company": "Yandex",
        "stack": "python",
        "salary": 220000
    }
]
```

`record` переводится как "запись".

То есть:

```text
одна строка таблицы = одна запись = один словарь
```

В проекте это нужно, чтобы FastAPI мог удобно вернуть данные как JSON.

### Обязателен ли `rename`

Код:

```python
grouped = grouped.rename(columns={"stack": "направление"})
```

Эта строка не обязательна для работы программы.

Она просто переименовывает столбец:

```text
stack -> направление
```

Если оставить `rename`, ответ будет таким:

```json
[
  {
    "направление": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

Если убрать `rename`, код все равно будет работать, но ответ будет таким:

```json
[
  {
    "stack": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

То есть меняется только название поля в JSON-ответе.

### Зачем нужен `plt.switch_backend("Agg")`

Код:

```python
plt.switch_backend("Agg")
```

Эта строка говорит matplotlib не открывать окно с графиком, а просто сохранять график в PNG-файл.

В проекте график создается здесь:

```python
plt.savefig("internship_salaries.png", dpi=150)
```

На обычном компьютере matplotlib иногда пытается открыть отдельное окно с графиком. Но для API это не нужно, потому что API должен вернуть файл.

Без `plt.switch_backend("Agg")` на некоторых компьютерах может быть ошибка Tkinter, например `TclError`.

Поэтому эту строку лучше оставить.

### Что делают два метода: `groupby_stack` и `median_salaries`

Метод `groupby_stack`:

```python
def groupby_stack(self):
    grouped = self.df.groupby("stack", as_index=False)["salary"].agg(
        количество="count",
        медианная_зарплата="median",
    )
    grouped = grouped.rename(columns={"stack": "направление"})
    return grouped.to_dict(orient="records")
```

Он нужен для endpoint:

```text
/vacancies/grouped
```

Он возвращает подробную статистику:

```json
[
  {
    "направление": "python",
    "количество": 4,
    "медианная_зарплата": 215000
  }
]
```

Метод `median_salaries`:

```python
def median_salaries(self):
    medians = self.df.groupby("stack")["salary"].median().sort_values(ascending=False)
    return {stack: int(salary) for stack, salary in medians.items()}
```

Он нужен для графика.

Он возвращает короткий словарь:

```python
{
    "data": 225000,
    "java": 215000,
    "python": 215000,
    "frontend": 180000,
    "qa": 167500
}
```

Строка:

```python
return {stack: int(salary) for stack, salary in medians.items()}
```

проходит по результату pandas и превращает его в обычный словарь Python.

`int(salary)` убирает `.0`.

Например:

```python
215000.0
```

становится:

```python
215000
```
