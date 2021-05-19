from flask import Blueprint, render_template
from flask import session, g
from studycam.models import User_02
from studycam import db
# from mytools.analyzer import GetGraph


bp = Blueprint('mydata', __name__, url_prefix='/mydata/')


@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User_02.query.get(user_id)


@bp.route('/')
def index():
    query_mydata = db.engine.execute(f"SELECT   operationTime / 60"
                                     f'       , totalWorkingTime / 60'
                                     f'       , totalWorkingTime / operationTime * 100'
                                     f'       , blinkCount / totalWorkingTime * 60'
                                     f'       , warningCount / totalWorkingTime * 60'
                                     f'       , alertCount/ totalWorkingTime * 60'
                                     f'       , create_date '
                                     f'FROM     usage_02 '
                                     f'WHERE    username = "{g.user.username}" '
                                     f'ORDER BY id desc')
    all_rows = [row for row in query_mydata]
    all_rows = all_rows[:10]
    return render_template('mydata/index.html', result=all_rows)


@bp.route('/bydate/')
def bydate():
    query_mydata = db.engine.execute(f"SELECT SUM(operationTime) / 60"
                                     f'     , SUM(totalWorkingTime) / 60'
                                     f'     , SUM(totalWorkingTime) / SUM(operationTime) * 100'
                                     f'     , SUM(blinkCount) / SUM(totalWorkingTime) * 60'
                                     f'     , SUM(warningCount)/ SUM(totalWorkingTime) * 60'
                                     f'     , SUM(alertCount)/ SUM(totalWorkingTime) * 60'
                                     f'     , create_date '
                                     f'FROM usage_02 '
                                     f'WHERE username = "{g.user.username}" '
                                     f'GROUP BY create_date '
                                     f'ORDER BY create_date desc')
    all_rows = [row for row in query_mydata]

    return render_template('mydata/bydate.html', result=all_rows)


@bp.route('/byweek/')
def byweek():
    query_mydata = db.engine.execute(f"SELECT SUM(operationTime) / 60"
                                     f'     , SUM(totalWorkingTime) / 60'
                                     f"     , SUM(totalWorkingTime) / SUM(operationTime) * 100"
                                     f'     , SUM(blinkCount) / SUM(totalWorkingTime) * 60'
                                     f'     , SUM(warningCount)/ SUM(totalWorkingTime) * 60'
                                     f'     , SUM(alertCount)/ SUM(totalWorkingTime) * 60'
                                     f'     , WEEKDAY(create_date) '
                                     f'FROM usage_02 '
                                     f'WHERE username = "{g.user.username}" '
                                     f'GROUP BY WEEKDAY(create_date) '
                                     f'ORDER BY WEEKDAY(create_date)')
    weekname = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

    all_rows = [row for row in query_mydata]
    # GetGraph(all_rows, 6, 2)

    return render_template('mydata/byweek.html', result=all_rows, weekname=weekname)


@bp.route('/detail/')
def detail():
    global mydataList
    mydataDf = pd.DataFrame(mydataList,
                            columns=[
                                'id',
                                'username',
                                'operationTime',
                                'totalWorkingTime',
                                'longestOpenedTime',
                                'blinkCount',
                                'warningCount',
                                'alertCount',
                                'create_date'
                            ])
    mydataDf.drop(['id', 'username'], inplace=True)
    return render_template('mydata/detail.html', data=mydataList, mydataDf=mydataDf)