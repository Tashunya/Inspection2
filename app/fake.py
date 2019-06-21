from random import uniform
from . import db
from .models import Node, Measurement


parent_nodes = Node.query.filter_by(boiler_id=1).with_entities(Node.parent_id).distinct().all()
parent_nodes = [node.parent_id for node in parent_nodes if node.parent_id != None]
nodes = Node.query.filter(~Node.id.in_(parent_nodes)).all()


def add_measurements(node_list):

    years = ['2016-06-15', '2017-06-20', '2018-06-25']

    for year in years:
        for node in node_list:
            measurement = Measurement(boiler_id=node.boiler_id,
                                      node_id=node.id,
                                      measure_date=year,
                                      value=uniform(6.5, 4.5))
            db.session.add(measurement)

    db.session.commit()




