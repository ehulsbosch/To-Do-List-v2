from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt, timedelta


engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return f'Table Name: {self.__tablename__}.\n' \
               f'Column id: {self.id}.\n' \
               f'Column task: {self.task}\n' \
               f'Column deadline: {self.deadline}'


Base.metadata.create_all(engine)


class DB:
    @staticmethod
    def gettasks(date_start=None, date_end=None):
        if date_start and date_end:
            res = session.query(Table).filter(Table.deadline >= date_start).\
                filter(Table.deadline <= date_end).order_by(Table.deadline).all()
        elif date_start:
            res = session.query(Table).filter(Table.deadline >= date_start).\
                order_by(Table.deadline).all()
        elif date_end:
            res = session.query(Table).filter(Table.deadline <= date_end).\
                order_by(Table.deadline).all()
        else:
            res = session.query(Table).order_by(Table.deadline).all()
        return res

    @staticmethod
    def addtask(task, deadline=datetime.today()) -> bool:
        task = Table(task=task, deadline=deadline)
        session.add(task)
        session.commit()
        return True

    @staticmethod
    def delete(task) -> bool:
        session.query(Table).filter_by(id=task.id).delete()
        session.commit()
        return True


class Menu:
    def __init__(self):
        self.task = []

    def __str__(self):
        return '1) Today\'s tasks\n' \
               '2) Week\'s tasks\n' \
               '3) All tasks\n' \
               '4) Missed tasks\n' \
               '5) Add task\n' \
               '6) Delete task\n' \
               '0) Exit'

    def getinput(self):
        print(Menu())
        res: int = int(input())
        opts = {
            1: lambda: self.gettasks('today'),
            2: lambda: self.gettasks('week'),
            3: lambda: self.gettasks('all'),
            4: lambda: self.gettasks('missed'),
            5: lambda: self.addtask(),
            6: lambda: self.deletetask(),
            0: lambda: exit('Bye!')
        }
        opts[res]()

    def gettasks(self, _time: str = 'today', return_only=False):
        _today = dt.today().date()
        opts = {
            'today': lambda: DB().gettasks(_today, _today + timedelta(days=0)),
            'week': lambda: DB().gettasks(_today, _today + timedelta(days=7)),
            'missed': lambda: DB().gettasks(date_end=_today - timedelta(days=1)),
            'all': lambda: DB().gettasks()
        }
        tasklist = opts.get(_time, 'Invalid')
        if return_only:
            return tasklist
        else:
            self.__printtasks(_time, tasklist, _today)

        self.getinput()

    def addtask(self):
        print('\nEnter task')
        res: str = input()
        print('Enter deadline')
        _date = input()
        print(_date)
        try:
            _date = dt.strptime(_date, '%Y-%m-%d')
        except:
            _date = dt.today()
        finally:
            if DB().addtask(res, _date):
                print('The task has been added!')
        self.getinput()

    def deletetask(self):
        tasks = self.gettasks('all', True)()
        if not tasks:
            print('No tasks!')
        else:
            print('Choose the number of the task you want to delete:')
            for key, value in enumerate(tasks):
                print(f'{key + 1}. {value.task}. {value.deadline.strftime("%d %b")}')
            _delete: int = int(input())
            DB().delete(tasks[_delete-1])
        self.getinput()

    @staticmethod
    def __printtasks(_time: str, tasklist, _today):
        tasks = tasklist()
        def today():
            print(f'\nToday {_today.strftime("%-d %b")}: ')
            if not tasks:
                print('Nothing to do!')
            else:
                for key, value in enumerate(tasks):
                    print(f'{key + 1}. {value.task}')
            print('\n')

        def week():
            _alldays = dict()
            i = 0
            while i < 7:
                new_time = dt.strftime(_today + timedelta(days=i), '%Y-%m-%d')
                _alldays[new_time] = list()
                i += 1
            for key, value in enumerate(tasks):
                _alldays[dt.strftime(value.deadline, '%Y-%m-%d')].append(value)
            for k, v in enumerate(_alldays):

                print(f'\n{dt.strptime(v, "%Y-%m-%d").strftime("%A %-d %b")}:')
                # print(f'\n{v}')
                if not _alldays[v]:
                    print('Nothing to do!')
                for l, b in enumerate(_alldays[v]):
                    print(f'{l+1}. {b.task}')
            print ('\n')

        def _all():
            if not tasks:
                print('Nothing to do!')
            else:
                for key, value in enumerate(tasks):
                    print(f'{key + 1}. {value.task}. {value.deadline.strftime("%d %b")}')
            print('\n')

        opts = {
            'today': today,
            'week': week,
            'missed': _all,
            'all': _all
        }
        res = opts.get(_time, lambda: 'invalid input')
        res()


m = Menu()
m.getinput()



