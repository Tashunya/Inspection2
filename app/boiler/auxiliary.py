"""
Module is used to provide auxiliary functions for boiler views
Function add_node_to_db saves new boiler structure to db
Function allowed_file checks if given file has .csv extension
"""

from sqlalchemy.sql.expression import func
from .. import db
from ..models import Node, Norm


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
