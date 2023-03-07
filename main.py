# import sqlite3 as sq
# import pandas as pd
# import datetime
# import tkinter as tk
# from tkinter import ttk
# import tkcalendar
# from itertools import combinations
# from copy import deepcopy
# from tkinter import messagebox
# from hotel import User,Customer,Admin

from appgui import *

def check_for_tables(hoteldb,cursor):
    cursor.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' ''')
    return cursor.fetchone()

def create_tables(hoteldb):

    # hoteldb.execute('''DROP TABLE IF EXISTS customer;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS includes;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS checkin;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS room;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS room_type;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS user;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS admin;''')
    # hoteldb.execute('''DROP TABLE IF EXISTS reservation;''')

    hoteldb.execute(
        '''CREATE TABLE user 
        (user_id INTEGER NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        PRIMARY KEY(user_id));'''
    )
    hoteldb.execute(
        '''CREATE TABLE admin
        (user_id INTEGER UNIQUE NOT NULL,
        admin_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        added_by INTEGER,
        PRIMARY KEY(admin_id),
        FOREIGN KEY(user_id) references user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY(added_by) references admin(admin_id) ON DELETE SET NULL ON UPDATE CASCADE);'''
    ) #enas admin einai opwsdipote user opote NOT NULL se eksairesi me ton customer
    hoteldb.execute(
        '''CREATE TABLE customer 
        (customer_id INTEGER NOT NULL,
        user_id INTEGER UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_num INTEGER,
        PRIMARY KEY(customer_id),
        FOREIGN KEY(user_id) references user(user_id) ON DELETE CASCADE ON UPDATE CASCADE);''') #unique userid alla can be null
    hoteldb.execute(
        '''CREATE TABLE room
        (room_id INTEGER NOT NULL,
        room_type_id INTEGER NOT NULL,
        room_num INTEGER NOT NULL UNIQUE,
        floor INTEGER,
        PRIMARY KEY (room_id),
        FOREIGN KEY(room_type_id) references room_type(room_type_id) ON UPDATE CASCADE);
        ''')
    hoteldb.execute(
        '''CREATE TABLE room_type
        (room_type_id INTEGER NOT NULL,
        capacity INTEGER NOT NULL,
        pets BINARY,
        balcony BINARY,
        pricepernight INTEGER NOT NULL,
        PRIMARY KEY(room_type_id),
        CONSTRAINT roomtype_definition UNIQUE(capacity,pets,balcony));'''
    )  # unique giati den theloume diplotipes katigories
    hoteldb.execute(
        '''CREATE TABLE reservation
        (reservation_num INTEGER NOT NULL,
        customer_id INTEGER,
        num_of_people INTEGER,
        reservation_date DATE,
        total_price REAL,
        arrival_date DATE NOT NULL,
        departure_date DATE NOT NULL,
        PRIMARY KEY(reservation_num),
        FOREIGN KEY(customer_id) references customer(customer_id)
        ON DELETE SET NULL ON UPDATE CASCADE);''')  # an diagrafei o pelatis/profil aptin db den thes na diagrafei kai h kratiseis pou ekane
    hoteldb.execute(
        '''CREATE TABLE includes
        (reservation_number INTEGER NOT NULL,
        room_type_id INTEGER NOT NULL,
        num_of_rooms INTEGER NOT NULL,
        PRIMARY KEY(reservation_number,room_type_id),
        FOREIGN KEY(reservation_number) references reservation
        ON DELETE CASCADE,
        FOREIGN KEY(room_type_id) references room_type
        ON UPDATE CASCADE);'''
    )
    hoteldb.execute(
        '''CREATE TABLE checkin
        (reservation_num INTEGER NOT NULL,
        room_num INTEGER NOT NULL,
        by_admin INTEGER NOT NULL,
        time_of_arrival DATETIME,
        PRIMARY KEY(reservation_num,room_num),
        FOREIGN KEY(reservation_num) references reservation(reservation_num) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(room_num) references room(room_num) ON UPDATE CASCADE,
        FOREIGN KEY(by_admin) references admin(admin_id) ON UPDATE CASCADE);'''
    )

def load_excel_data_to_db(hoteldb):

    users_data = pd.read_excel("excel_data/users.xlsx", header=0)
    rooms_data = pd.read_excel("excel_data/rooms.xlsx", header=0)
    type_data = pd.read_excel("excel_data/room type.xlsx", header=0)
    admin_data=pd.read_excel("excel_data/admin.xlsx",header=0)

    users_data.to_sql('user', hoteldb, if_exists='append', index=False)
    type_data.to_sql('room_type', hoteldb, if_exists='append', index=False)
    rooms_data.to_sql('room', hoteldb, if_exists='append', index=False)
    admin_data.to_sql('admin',hoteldb,if_exists='append',index=False)



if __name__ == "__main__":
    db = sq.connect("hotel.db")
    c = db.cursor()
    db.execute('''PRAGMA foreign_keys=1''')
    db.commit()
    if not check_for_tables(db,c):
        create_tables(db)
        load_excel_data_to_db(db)

        first_demo_user=User(username="georgepetr",password="123456",firstname="GIORGOS",lastname="PETRAKIS")
        second_demo_user=User(username="dimos",password="2345",firstname="DIMOS",lastname="SAKELLARIOU")
        first_demo_user.add_to_db(db,c)
        second_demo_user.add_to_db(db,c)
        admin=Admin(user=second_demo_user)

        current = Customer(user=first_demo_user)
        arrival = datetime.date(2022, 6, 10)
        departure = datetime.date(2022, 6, 15)
        # eisagoume mia kratisi
        current.make_reservation(db, c, arrival, departure, [5], 1)


    w=App(db,c)
    w.mainloop()

