from random import uniform
import csv
from . import db
from .models import Node, Measurement

parent_nodes = Node.query.filter_by(boiler_id=1).with_entities(Node.parent_id).distinct().all()
parent_nodes = [node.parent_id for node in parent_nodes if node.parent_id != None]
nodes = Node.query.filter(~Node.id.in_(parent_nodes)).all()

years = ['2016-06-15', '2017-06-20', '2018-06-25', '2019-06-17']


def add_measurements(node_list, year, x, y):
    for node in node_list:
        measurement = Measurement(node_id=node.id,
                                  measure_date=year,
                                  value=round(uniform(x, y), 2))
        db.session.add(measurement)
    db.session.commit()


def fake_csv(num, x, y):
    name = f'fake_{str(num)}.csv'
    with open(name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(1, num+1):
            writer.writerow([i, round(uniform(x, y), 2)])
    csvfile.close()






