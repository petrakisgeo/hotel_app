import datetime
from collections import Counter


class User:

    def __init__(self, username, password, firstname=None, lastname=None):
        self.username = username
        self.password = password
        self.first_name = firstname
        self.last_name = lastname
        self.userid = None  # no id if he has not been added to users table

    def user_exists(self, cursor):
        cursor.execute("SELECT count(*) FROM user where username=?", (self.username,))
        a = cursor.fetchone()[0]
        print(a)
        return a  # 1 if yes 0 if no

    def check_credentials(self, cursor):
        cursor.execute("SELECT count(*) FROM user where username=? AND password=?", (self.username, self.password))
        res = cursor.fetchone()[0]
        if res:
            print("Valid username and password")
            cursor.execute("SELECT user_id FROM user where username=? AND password=?", (self.username, self.password))
            res = cursor.fetchone()[0]
            self.userid = res
        return res

    def add_to_db(self, hoteldb, cursor):
        if not self.user_exists(cursor):
            hoteldb.execute('''INSERT INTO user(username,password,first_name,last_name) VALUES (?,?,?,?)''',
                            (self.username, self.password, self.first_name, self.last_name))
            hoteldb.commit()
            cursor.execute(
                "SELECT user_id FROM user ORDER BY user_id DESC LIMIT 1")  # last id is this customers id
        else:
            cursor.execute("SELECT user_id FROM user WHERE username=?", (self.username,))  # gia auto unique usernames
        self.userid = cursor.fetchone()[0]
        return self.userid


class Customer(User):
    def __init__(self, user, phone=None):
        # PARADOXI: Den mporei na iparksei customer xwris user account stin efarmogi
        super().__init__(user.username, user.password, user.first_name, user.last_name)
        self.userid = user.userid
        print("initcharacter", self.userid)
        self.phone_num = phone

        self.customerid = None  # has no id if he has not been added to the customers table

    def add_to_db(self, hoteldb, cursor):  # for private use
        try:
            hoteldb.execute('''INSERT INTO customer(user_id,first_name, last_name, phone_num) VALUES (?,?,?,?)''',
                            (self.userid, self.first_name, self.last_name,
                             self.phone_num))  # userid->can be null if customer continues without registration
            hoteldb.commit()
            cursor.execute(
                "SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1")  # last id is this customers id
        except:
            cursor.execute("SELECT customer_id FROM customer WHERE user_id=?", (self.userid,))

        self.customerid = cursor.fetchone()[0]
        print(self.customerid)
        return self.customerid

    def make_reservation(self, hoteldb, cursor, arrival, departure, roomtypes: list, num_of_people):
        roomtypes = dict(Counter(roomtypes))
        price = 0
        for roomtype, num_of_rooms in roomtypes.items():
            cursor.execute("SELECT pricepernight FROM room_type WHERE room_type_id=?", (roomtype,))
            price += (cursor.fetchone()[0]) * num_of_rooms * (departure - arrival).days
        self.customerid = self.add_to_db(hoteldb,
                                         cursor)  # apla epistrefei to customer id an o xrhsths ehei pragmatopoihsei ksana kratisi
        reservation_query = '''INSERT INTO reservation(customer_id,reservation_date,num_of_people,total_price,arrival_date,departure_date)
            VALUES(?,?,?,?,?,?);'''
        hoteldb.execute(reservation_query,
                        (self.customerid, datetime.date.today(), num_of_people, price, arrival, departure))

        cursor.execute("SELECT reservation_num FROM reservation ORDER BY reservation_num DESC LIMIT 1")
        res_number = cursor.fetchone()
        # sqlite kanei autoincrement integer primary keys opote apla pairnoume to teleutaio
        # mporw na ftiaksw leksiko me {roomtype_id: num_of_rooms} kai na kanw for loop gia to insert
        for roomtype, num_of_rooms in roomtypes.items():
            includes_query = '''INSERT INTO includes VALUES(?,?,?);'''
            hoteldb.execute(includes_query, (res_number[0], roomtype, num_of_rooms))
            hoteldb.commit()

    def get_id(self, cursor):
        cursor.execute("SELECT customer_id FROM customer WHERE user_id=?", (self.userid,))
        self.customerid = cursor.fetchone()[0]
        return self.customerid


class Admin(User):

    def __init__(self, user, addedby=None):
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.added_by = addedby
        self.userid = user.userid
        self.adminid = None  # prostithetai apo tin sqlite

    def add_to_db(self, hoteldb, cursor):
        try:
            hoteldb.execute('''INSERT INTO admin(user_id,first_name, last_name, added_by) VALUES (?,?,?,?)''',
                            (self.userid, self.first_name, self.last_name, self.added_by))
            hoteldb.commit()
            cursor.execute(
                "SELECT admin_id FROM admin ORDER BY admin_id DESC LIMIT 1")  # last id is this customers id
        except:
            print("User already in admin database")  #
            cursor.execute("SELECT admin_id FROM admin WHERE admin_id=?", (self.adminid))
        self.adminid = cursor.fetchone()[0]
        return self.adminid

    def get_id(self, cursor):
        cursor.execute("SELECT admin_id FROM admin WHERE user_id=?", (self.userid,))
        self.adminid = cursor.fetchone()[0]
        return self.adminid
