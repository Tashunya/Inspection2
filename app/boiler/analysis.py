from sqlalchemy.sql.expression import func, and_
from sqlalchemy.orm import aliased
from .. import db
from ..models import Node, Norm, Measurement


def get_analysis_data(parent_id):
    """
    Provides analysis of average thickness and average thinning of given parent node's children nodes and
    give predictions for the next 2 years based on analysis
    :param parent_id:
    :return: dict
    """
    result = {"avg_thickness": 0,
                  "avg_thinning": 0,
                  "stacked_bar": {
                      "labels": [],
                      "thickness": [],
                      "thinning": []},
                  "pie": {
                      "2019": [80, 30, 15, 5],
                      "2017": [80, 30, 15, 5],
                      "2016": [80, 30, 15, 5],
                      "2015": [80, 30, 15, 5],
                      "2014": [80, 30, 15, 5]}
                  }

    # get years, avg thickness and avg thinning
    prev_measurements = aliased(Measurement)
    year = func.extract('year', Measurement.measure_date).label("year")
    prev_year = func.extract('year', prev_measurements.measure_date).label("prev_year")
    current_avg = func.avg(Measurement.value).label("avg_thick")
    prev_avg = func.avg(prev_measurements.value).label("prev_avg_thick")

    thicknesses = db.session.query(year, current_avg, (prev_avg - current_avg).label("diff")). \
        join(Node, Node.id == Measurement.node_id).outerjoin(prev_measurements,
                                                             and_(Measurement.node_id == prev_measurements.node_id,
                                                                  year == prev_year + 1)). \
        filter(Node.parent_id == parent_id).group_by(year, prev_year)

    if len(thicknesses.all()) > 4:
        thicknesses = thicknesses[-4:]

    # calculations for stacked bar
    labels = []
    thickness = []
    thinning = []

    for year, avg_thickness, diff_thinning in thicknesses.all():
        labels.append(int(year))
        thickness.append(round(avg_thickness, 2))
        thinning.append(abs(round(diff_thinning, 2)) if diff_thinning is not None else 0)

    # get average thickness
    result["avg_thickness"] = thickness[-1]

    # get average thinning
    avg_thinning = round((sum(thinning) / len(thinning)), 2)
    result["avg_thinning"] = avg_thinning

    # add predictions for next 2 years
    for i in range(2):
        labels.append(labels[-1] + 1)
        thickness.append(thickness[-1] - avg_thinning)
        thinning.append(avg_thinning)

    result["stacked_bar"]["labels"] = labels
    result["stacked_bar"]["thickness"] = thickness
    result["stacked_bar"]["thinning"] = thinning

    # get data for pie

    # calculations

    return
