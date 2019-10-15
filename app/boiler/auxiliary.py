"""
Module is used to provide auxiliary functions for boiler views
Function add_node_to_db saves new boiler structure to db
Function allowed_file checks if given file has .csv extension
"""

from sqlalchemy.sql.expression import func, and_, case
from sqlalchemy.orm import aliased
from .. import db
from ..models import Node, Norm, Measurement


def add_nodes_to_db(boiler_structure, boiler_id):
    """
    Adds newly created boiler structure to db
    :param boiler_structure:
    :param boiler_id:
    :return: None
    """

    last_id = db.session.query(func.max(Node.id)).first()[0]

    if last_id == None:
        current_id = 1
    else:
        current_id = last_id + 1

    for block in boiler_structure:
        new_block = Node(boiler_id=boiler_id,
                         index=block.get('index'),
                         node_name=block.get('node_name'),
                         id=current_id
                         )
        db.session.add(new_block)
        current_id += 1

        for child_1 in block.get('children'):
            new_child_1 = Node(boiler_id=boiler_id,
                               parent_id=new_block.id,
                               index=child_1.get('index'),
                               node_name=child_1.get('node_name'),
                               id=current_id
                               )
            db.session.add(new_child_1)
            current_id += 1

            for child_2 in child_1.get('children'):
                new_child_2 = Node(boiler_id=boiler_id,
                                   parent_id=new_child_1.id,
                                   index=child_2.get('index'),
                                   node_name=child_2.get('node_name'),
                                   id=current_id
                                   )
                db.session.add(new_child_2)
                current_id += 1

                for element in range(1, int(child_2.get("Elements")) + 1):
                    for point in range(1, int(child_2.get("Points")) + 1):
                        new_point = Node(boiler_id=boiler_id,
                                         parent_id=new_child_2.id,
                                         index=point,
                                         node_name='Element ' + str(element)
                                         + ' Point ' + str(point),
                                         id=current_id
                                         )
                        db.session.add(new_point)
                        new_point_norm = Norm(node_id=current_id,
                                              default=6.5,
                                              minor=6.0,
                                              major=5.2,
                                              defect=4.5)
                        db.session.add(new_point_norm)

                        current_id += 1
    db.session.commit()


def allowed_file(filename):
    """
    Checks if uploaded file extension is csv
    :param filename:
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'csv'


def get_analysis_data(parent_id):
    """
    Provides analysis of average thickness and average thinning of given parent node's children nodes and
    give predictions for the next 2 years based on analysis
    :param parent_id:
    :return: dict
    """
    result = {"avg_thickness": 0,
              "avg_thinning": 0,
              "last_year": 0,
              "stacked_bar": {
                  "labels": [],
                  "thickness": [],
                  "thinning": []},
              "pie": {}
              }

    prev_measurements = aliased(Measurement)
    year = func.extract('year', Measurement.measure_date).label("year")
    prev_year = func.extract('year', prev_measurements.measure_date).label("prev_year")
    current_avg = func.avg(Measurement.value).label("avg_thick")
    prev_avg = func.avg(prev_measurements.value).label("prev_avg_thick")

    # get years, avg thickness and avg thinning
    thicknesses = db.session.query(year, current_avg, (prev_avg - current_avg).label("diff")). \
        join(Node, Node.id == Measurement.node_id). \
        outerjoin(prev_measurements, and_(Measurement.node_id == prev_measurements.node_id,
                                          year == prev_year + 1)). \
        filter(Node.parent_id == parent_id).group_by(year, prev_year).order_by(year, prev_year)

    if len(thicknesses.all()) > 4:
        thicknesses = thicknesses.all()[-4:]
    else:
        thicknesses = thicknesses.all()

    # calculations for stacked bar
    labels = []
    thickness = []
    thinning = []

    for year, avg_thickness, diff_thinning in thicknesses:
        labels.append(int(year))
        thickness.append(round(avg_thickness, 2))
        thinning.append(abs(round(diff_thinning, 2)) if diff_thinning is not None else 0)

    # get average thickness
    result["avg_thickness"] = thickness[-1]

    # get average thinning
    avg_thinning = round((sum(thinning) / len(thinning)), 2)
    result["avg_thinning"] = avg_thinning

    # get last year of measurements
    result["last_year"] = labels[-1]

    # add predictions for next 2 years
    for i in range(2):
        labels.append(labels[-1] + 1)
        thickness.append(thickness[-1] - avg_thinning)
        thinning.append(avg_thinning)

    result["stacked_bar"]["labels"] = labels
    result["stacked_bar"]["thickness"] = thickness
    result["stacked_bar"]["thinning"] = thinning

    # get data for pie
    # compare value with norms and define it to one of 4 groups
    category = case([(and_(Measurement.value > Norm.minor, Measurement.value <= Norm.default), 0),
                     (and_(Measurement.value > Norm.major, Measurement.value <= Norm.minor), 1),
                     (and_(Measurement.value > Norm.defect, Measurement.value <= Norm.major), 2)],
                    else_=3).label("category")

    # get data
    year = func.extract('year', Measurement.measure_date).label("year")
    pie_data = db.session.query(year, category, func.count(1).label("cnt")). \
        join(Node, Node.id == Measurement.node_id).join(Norm, Norm.node_id == Measurement.node_id). \
        filter(Node.parent_id == parent_id).group_by(year, category)

    # calculations
    pie = {}

    for year, cat, num in pie_data.all():
        year = str(int(year))
        if year not in pie:
            pie[year] = [0, 0, 0, 0]
        pie[year][cat] = num

    result["pie"] = pie

    return result