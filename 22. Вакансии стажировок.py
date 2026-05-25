import json

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse


plt.switch_backend("Agg")


class InternshipBoard:
    def __init__(self):
        self.df = pd.read_csv("internships.csv")

    def records(self, df):
        records = []
        for item in df.to_dict(orient="records"):
            records.append(
                {
                    "компания": item["company"],
                    "направление": item["stack"],
                    "зарплата": item["salary"],
                }
            )
        return records

    def vacancies_table(self):
        return self.records(self.df)

    def filter_by_stack(self, stack):
        filtered = self.df[self.df["stack"].str.lower() == stack.lower()]
        return self.records(filtered)

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

    def groupby_stack(self):
        grouped = self.df.groupby("stack", as_index=False)["salary"].agg(
            количество="count",
            медианная_зарплата="median",
        )
        grouped = grouped.rename(columns={"stack": "направление"})
        return grouped.to_dict(orient="records")

    def median_salaries(self):
        medians = self.df.groupby("stack")["salary"].median().sort_values(ascending=False)
        return {stack: int(salary) for stack, salary in medians.items()}

    def save_salary_chart(self):
        medians = self.median_salaries()

        plt.figure(figsize=(9, 5))
        plt.bar(medians.keys(), medians.values(), color="green")
        plt.title("Медианная зарплата стажировок по направлениям")
        plt.xlabel("Направление")
        plt.ylabel("Медианная зарплата")
        plt.savefig("internship_salaries.png", dpi=150)
        plt.close()

        return "internship_salaries.png"


app = FastAPI(title="API вакансий стажировок")


@app.get("/vacancies")
def vacancies():
    return InternshipBoard().vacancies_table()


@app.get("/vacancies/filter")
def vacancies_filter(stack: str = Query(...)):
    return InternshipBoard().generate_json_by_stack(stack)


@app.get("/vacancies/grouped")
def vacancies_grouped():
    return InternshipBoard().groupby_stack()


@app.get("/vacancies/chart")
def vacancies_chart():
    path = InternshipBoard().save_salary_chart()
    return FileResponse(path, media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    print("Docs: http://127.0.0.1:8010/docs")
    uvicorn.run(app, host="127.0.0.1", port=8010)
