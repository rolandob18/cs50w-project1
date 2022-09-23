from asyncore import read
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

url = create_engine ("postgresql://setruvhdhepzne:14dde31f92e7cfd1bed1083f125402dc352cd503bc851057fccddafca4b5c551@ec2-34-227-135-211.compute-1.amazonaws.com:5432/dd7jm4tkdkdbed")

db = scoped_session(sessionmaker(bind=url))

f = open("books.csv")

leer = csv.reader(f)

for isbn,title,author,year in leer:
    print(isbn,title,author,year)
    db.execute("INSERT INTO libros (isbn,title,author,year) VALUES (:isbn , :title , :author , :year)", {"isbn":isbn, "title": title, "author": author, "year": year})
    db.commit()