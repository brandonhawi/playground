from pathlib import Path

import duckdb

HF_PARQUET = "hf://datasets/brandonhawi/nbadb/parquet"
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "nba.duckdb"


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    files = con.sql(f"SELECT file FROM glob('{HF_PARQUET}/*.parquet')").fetchall()
    for (url,) in files:
        name = url.rsplit("/", 1)[-1].removesuffix(".parquet")
        con.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{url}')")
        print(f"created view: {name}")
    con.close()


if __name__ == "__main__":
    main()
