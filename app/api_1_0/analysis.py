"""
This module provides one function - get_analysis_data()
to get data for analytics from db
"""

from sqlalchemy.sql.expression import func, and_, case
from sqlalchemy.orm import aliased
from .. import db
from ..models import Node, Norm, Measurement


def get_analysis_data(parent_id):
    """
    Provides analysis of average thickness and average thinning of given
    parent node's children nodes and gives predictions
    for the next 2 years based on analysis
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
    prev_year = func.extract('year', prev_measurements.measure_date).\
        label("prev_year")
    current_avg = func.avg(Measurement.value).label("avg_thick")
    prev_avg = func.avg(prev_measurements.value).label("prev_avg_thick")

    # get years, avg thickness and avg thinning
    thicknesses = db.session.query(year, current_avg,
                                   (prev_avg - current_avg).label("diff")). \
        join(Node, Node.id == Measurement.node_id). \
        outerjoin(prev_measurements,
                  and_(Measurement.node_id == prev_measurements.node_id,
                                          year == prev_year + 1)). \
        filter(Node.parent_id == parent_id).group_by(year, prev_year). \
        order_by(year, prev_year)

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
        thinning.append(abs(round(diff_thinning, 2))
                        if diff_thinning is not None else 0)

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
    category = case([(and_(Measurement.value > Norm.minor,
                           Measurement.value <= Norm.default), 0),
                     (and_(Measurement.value > Norm.major,
                           Measurement.value <= Norm.minor), 1),
                     (and_(Measurement.value > Norm.defect,
                           Measurement.value <= Norm.major), 2)],
                    else_=3).label("category")

    # get data
    year = func.extract('year', Measurement.measure_date).label("year")
    pie_data = db.session.query(year, category, func.count(1).label("cnt")). \
        join(Node, Node.id == Measurement.node_id). \
        join(Norm, Norm.node_id == Measurement.node_id). \
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
