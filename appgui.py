import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
import tkcalendar
import sqlite3 as sq
import pandas as pd
from copy import deepcopy
from itertools import combinations
from collections import Counter
from hotel import User, Customer, Admin
from tkinter import messagebox

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.rcParams['ytick.labelsize'] = 'small'
matplotlib.rcParams['xtick.labelsize'] = 'x-small'
# colors
co1 = "white"
co2 = "blue"
co3 = "#6074FF"


def find_scenarios(database, cursor, arrival_date, departure_date, num_of_people, num_of_rooms=5, balcony=0, pets=0):
    available_query = '''
            SELECT room_type_id,capacity,available_rooms
            FROM(SELECT *, (SELECT count(*) from room where room.room_type_id=r.room_type_id) -
                      ifnull((SELECT sum(num_of_rooms) from (includes join reservation on includes.reservation_number = reservation.reservation_num) as e
                      where e.room_type_id=r.room_type_id
                      and ((?1 between arrival_date and departure_date)
                      or (?2 between arrival_date and departure_date)
                      or (arrival_date between ?1 and ?2)
                      or (departure_date between ?1 and ?2))),0) as available_rooms
                from room_type as r
                where available_rooms>0) '''
    ordering_string = '''ORDER BY pricepernight ASC, capacity DESC'''
    if balcony and not pets:
        filter = '''WHERE balcony IS NOT NULL '''
    elif pets and not balcony:
        filter = '''WHERE pets IS NOT NULL '''
    elif pets and balcony:
        filter = '''WHERE pets IS NOT NULL AND balcony IS NOT NULL '''
    else:
        filter = ''' '''
    final_query = available_query + filter + ordering_string
    cursor.execute(final_query, (arrival_date, departure_date))

    available_capacities = []  # plhroforia gia to posa dwmatia ehoume ana xwrhtikothta gia na vroume ta senaria filoksenias
    capacities_dict = {}  # ta roomtype_ids taksinomimena
    for result in cursor.fetchall():
        available_capacities += [result[1]] * result[2]
        capacities_dict[result[1]] = capacities_dict.get(result[1], []) + [result[0]] * result[2]
    senaria = [com for i in range(num_of_rooms) for com in combinations(available_capacities, i) if
               sum(com) == num_of_people]
    apodekta = []
    for i in senaria:
        if (i not in apodekta) and (sum(i) == num_of_people):
            apodekta.append(i)  # diathrei price order!
    roomtype_id_senaria = []
    for senario in apodekta:
        ids = []
        d = deepcopy(capacities_dict)
        for capacity in senario:
            ids.append(d[capacity].pop(0))
        roomtype_id_senaria += [ids]
    return roomtype_id_senaria


def make_reservation(database, cursor, arrival_date, departure_date, roomtypeids, customerid, num_of_people):
    roomtypeids = dict(Counter(roomtypeids))
    reservation_query = '''INSERT INTO reservation(customer_id,reservation_date)
    VALUES(?,?);'''
    database.execute(reservation_query, (customerid, datetime.date.today()))  # num of rooms apo input

    cursor.execute("SELECT reservation_num FROM reservation ORDER BY reservation_num DESC LIMIT 1")
    res_number = cursor.fetchone()
    # sqlite kanei autoincrement integer primary keys opote apla pairnoume to teleutaio
    # mporw na ftiaksw leksiko me {roomtype_id: num_of_rooms} kai na kanw for loop gia to insert
    for roomtype, num_of_rooms in roomtypeids.items():
        includes_query = '''INSERT INTO includes VALUES(?,?,?,?,?);'''
        database.execute(includes_query, (res_number[0], roomtype, num_of_rooms, arrival_date, departure_date))
        database.commit()


class loginWindow(tk.Toplevel):

    def __init__(self, parent, title, dimensions, hoteldb, cursor, user_handler, admin_handler):
        super().__init__(parent)

        self.title(title)
        self.geometry(dimensions)
        self.resizable(width=False, height=False)
        self.configure(bg=co1)
        self.hoteldb = hoteldb
        self.cursor = cursor
        self.succesful_user_login_method = user_handler  # pass userid to main app
        self.succesful_admin_login_method = admin_handler

        # frames
        self.frame_up = tk.Frame(self, width=310, height=50, bg=co1)
        self.frame_up.grid(row=0, column=0)

        self.frame_down = tk.Frame(self, width=310, height=600, bg=co1)
        self.frame_down.grid(row=1, column=0)

        # frame_up widgets

        self.heading = tk.Label(self.frame_up, text="Σύνδεση", bg=co1, font=('Poppins 23'))
        self.heading.place(x=5, y=5)

        self.line = tk.Label(self.frame_up, width=40, text="", height=1, bg=co3, )
        self.line.place(x=10, y=45)

        # frame_down widgets

        self.e_name = tk.Label(self.frame_down, text="Όνομα *", height=1, bg=co1, fg=co2, font=('Poppins 12'))
        self.e_name.place(x=10, y=10)
        self.fname_entry = tk.Entry(self.frame_down, width=25, justify='left', font=("", 15), highlightthickness=1)
        self.fname_entry.place(x=14, y=50)

        self.e_lname = tk.Label(self.frame_down, text="Επίθετο *", height=1, bg=co1, fg=co2, font=('Poppins 12'))
        self.e_lname.place(x=10, y=95)
        self.lname_entry = tk.Entry(self.frame_down, width=25, justify='left', font=("", 15), highlightthickness=1)
        self.lname_entry.place(x=14, y=135)

        self.e_username = tk.Label(self.frame_down, text="Όνομα Χρήστη *", height=1, bg=co1, fg=co2,
                                   font=('Poppins 12'))
        self.e_username.place(x=10, y=180)
        self.username_entry = tk.Entry(self.frame_down, width=25, justify='left', font=("", 15), highlightthickness=1)
        self.username_entry.place(x=14, y=220)

        self.e_password = tk.Label(self.frame_down, text="Κωδικός *", height=1, bg=co1, fg=co2, font=('Poppins 12'))
        self.e_password.place(x=10, y=265)
        self.password_entry = tk.Entry(self.frame_down, width=25, justify='left', show='*', font=("", 15),
                                       highlightthickness=1)
        self.password_entry.place(x=14, y=305)

        self.login_button1 = tk.Button(self.frame_down, text="User Login", bg=co3, fg=co1, width=10, height=2,
                                       font=("Ivy 9 bold"))
        self.login_button1.place(x=15, y=400)
        self.login_button1 = tk.Button(self.frame_down, text="User Login", bg=co3, fg=co1, width=10, height=2,
                                       font=("Ivy 9 bold"), command=self.user_login)
        self.login_button1.place(x=15, y=400)

        self.login_button2 = tk.Button(self.frame_down, text="Admin Login", bg=co3, fg=co1, width=10, height=2,
                                       font=("Ivy 9 bold"))
        self.login_button2.place(x=15, y=440)
        self.login_button2 = tk.Button(self.frame_down, text="Admin Login", bg=co3, fg=co1, width=10, height=2,
                                       font=("Ivy 9 bold"), command=self.admin_login)
        self.login_button2.place(x=15, y=440)

        self.register_button = tk.Button(self.frame_down, text="Register", bg=co3, fg=co1, width=10, height=2,
                                         font=("Ivy 9 bold"))
        self.register_button.place(x=15, y=480)
        self.register_button = tk.Button(self.frame_down, text="Register", bg=co3, fg=co1, width=10, height=2,
                                         font=("Ivy 9 bold"), command=self.register_user)
        self.register_button.place(x=15, y=480)

    def user_login(self, *args):
        [username, password, _, _] = self.get_data()
        user = User(username, password)
        uid = user.check_credentials(self.cursor)
        print("Userid is", uid)
        if uid:
            self.cursor.execute("SELECT first_name,last_name FROM user where user_id=?", (uid,))
            name = self.cursor.fetchone()
            messagebox.showinfo(message=f'Welcome {name[0]}!')
            self.succesful_user_login_method(user)  # pass userid to main application
            self.destroy()
        else:
            messagebox.showinfo(message="Wrong username or password")

    def admin_login(self, *args):
        [username, password, _, _] = self.get_data()
        user = User(username, password)
        uid = user.check_credentials(self.cursor)
        if uid:
            admin_check = self.cursor.execute("SELECT count(*) FROM admin where user_id=?", (uid,))
            if admin_check:
                self.cursor.execute("SELECT first_name,last_name FROM user WHERE user_id=?", (uid,))
                name = self.cursor.fetchone()
                self.succesful_admin_login_method(user)
                messagebox.showinfo(message=f'Welcome {name[0]}!')
                self.destroy()
            else:
                messagebox.showinfo(message="User does not have admin privileges")
        else:
            messagebox.showinfo(message="Wrong username or password")

    def register_user(self, *args):
        [username, password, fname, lname] = self.get_data()
        user = User(username, password, fname, lname)
        if user.check_credentials(self.cursor):
            messagebox.showinfo(message="Username already exists")
        else:
            userid = user.add_to_db(self.hoteldb, self.cursor)
            messagebox.showinfo(message=f'Registration succesful, Welcome {fname}')
            self.succesful_user_login_method(user)
            self.destroy()

    def get_data(self):
        return [self.username_entry.get(), self.password_entry.get(), self.fname_entry.get(), self.lname_entry.get()]


class App(tk.Tk):

    def __init__(self, hoteldb, cursor, *args, **kwargs):
        tk.Tk.__init__(self, *args, *kwargs)

        self.state(newstate='iconic')  # start minimized
        self.title("My Hotel App")
        self.geometry("1300x350")
        self.tabcontrol = ttk.Notebook(self)
        self.tabcontrol.pack()

        self.hoteldb = hoteldb
        self.cursor = cursor
        self.last_search_results = []

        uw = loginWindow(self, "Login or Register", "310x600", self.hoteldb, self.cursor, self.get_userid,
                         self.get_adminid)
        uw.grab_set()

    def make_search_tab(self):
        self.tab1 = tk.Frame(self.tabcontrol)
        self.frame1 = tk.Frame(self.tab1)
        self.frame1.pack(side="top")
        self.frame2 = tk.Frame(self.tab1)
        self.frame2.pack(side="bottom")
        self.tabcontrol.add(self.tab1, text="Αναζήτηση")

        tmrw = datetime.date.today() + datetime.timedelta(days=1)
        self.arrival_entry = tkcalendar.DateEntry(self.frame1, width=10, selectmode='day',
                                                  mindate=datetime.date.today(), date_pattern='yyyy-mm-dd')
        self.arrival_entry.bind('<<DateEntrySelected>>', lambda event: self.refresh_departure_entry(self))
        self.arrival_entry.pack(side="left")
        self.departure_entry = tkcalendar.DateEntry(self.frame1, width=10, selectmode='day',
                                                    date_pattern='yyyy-mm-dd')
        self.departure_entry.pack(side="left", padx=5)

        self.num_of_ppl_entry = tk.Entry(self.frame1, width=5)
        self.num_of_ppl_entry.insert(0, '0')
        self.num_of_ppl_entry.pack(side="left", padx=10)

        self.button1 = tk.Button(self.frame1, text="Search for rooms", command=self.get_room_results)
        self.button1.pack(side="left")

        self.var1 = tk.IntVar()
        self.var2 = tk.IntVar()
        self.c1 = tk.Checkbutton(self.frame1, text='Μπαλκόνι;', variable=self.var1,
                                 onvalue=1, offvalue=0)

        self.c1.pack(side='left')
        self.c2 = tk.Checkbutton(self.frame1, text='Κατοικίδιο;', variable=self.var2,
                                 onvalue=1, offvalue=0)
        self.c2.pack(side='left')

        self.button2 = tk.Button(self.frame1, text="Προβολή σεναρίου φιλοξενίας", command=self.display_result)
        self.button2.pack(side="right")

        self.optionvar = tk.StringVar(self.frame1)
        self.selector = ttk.OptionMenu(self.frame1, self.optionvar)
        self.selector.config(width=5)
        self.selector.pack(side="right")

        self.roomsView = ttk.Treeview(master=self.frame2,
                                      columns=["room_id", "capacity", "pets", "balcony", "price/night", "total"])
        self.roomsView.pack(side="top", pady=4)
        self.roomsView.heading("room_id", text="Room Type ID")
        self.roomsView.heading("capacity", text="Χωρητικότητα δωματίου")
        self.roomsView.heading("pets", text="Επιτρέπονται κατοικίδια")
        self.roomsView.heading("balcony", text="Διαθέτει μπαλκόνι")
        self.roomsView.heading("price/night", text="Τιμή διανυκτεύρευσης")
        self.roomsView.heading("total", text="Σύνολο")
        self.roomsView['show'] = 'headings'

        self.reservation_button = tk.Button(self.frame2, text="Πραγματοποίηση κράτησης",
                                            command=self.confirm_reservation)
        self.reservation_button.pack(side='bottom')

    def make_reservations_tab(self):
        self.tab2 = tk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.tab2, text="Οι κρατήσεις μου")
        res_frame = tk.Frame(self.tab2)
        res_frame.grid(row=0, column=0)

        room_frame = tk.Frame(self.tab2)
        room_frame.grid(row=1, column=0)

        button_frame = tk.Frame(self.tab2)
        button_frame.grid(column=1, rowspan=2)

        self.resview = ttk.Treeview(master=res_frame,
                                    columns=["Αριθμός κράτησης", "ID χρήστη", "Αριθμός ατόμων",
                                             "Ημ.Κράτησης", "Τιμή", "Ημ.Άφιξης", "Ημ.Αναχώρησης"], height=6)
        self.resview.pack(side="left")
        self.resview.heading("Αριθμός κράτησης", text="Αριθμός κράτησης")
        self.resview.heading("ID χρήστη", text="ID χρήστη")

        self.resview.heading("Αριθμός ατόμων", text="Αριθμός ατόμων")

        self.resview.heading("Ημ.Κράτησης", text="Ημ. κράτησης")
        self.resview.heading("Τιμή", text="Τιμή")
        self.resview.heading("Ημ.Άφιξης", text="Ημ. άφιξης")
        self.resview.heading("Ημ.Αναχώρησης", text="Ημ. αναχώρησης")

        self.resview['show'] = 'headings'

        self.roomsview2 = ttk.Treeview(master=room_frame,
                                       columns=["room_id", "capacity", "numofrooms"])
        self.roomsview2.pack()
        self.roomsview2.heading("room_id", text="Room Type ID")
        self.roomsview2.heading("capacity", text="Χωρητικότητα δωματίου")
        self.roomsview2.heading("numofrooms", text="Αριθμός δωματίων")
        self.roomsview2['show'] = 'headings'

        res_button = tk.Button(button_frame, text="Εμφάνιση Κρατήσεων", command=self.display_reservations)
        res_button.pack(side="top")

        room_button = tk.Button(button_frame, text="Λεπτομέρειες Κράτησης", command=self.display_res_details)
        room_button.pack(side="top")

        cancel_button = tk.Button(button_frame, text="Ακύρωση Κράτησης", command=self.delete_reservation)
        cancel_button.pack(side="top")

    def make_checkin_tab(self):
        self.tab1 = tk.Frame(self.tabcontrol)
        self.frame1 = tk.Frame(self.tab1)
        self.frame1.pack(side="left")
        self.tabcontrol.add(self.tab1, text="Καταχώρηση Check-in")

        self.reservation_id_entry = tk.Entry(self.frame1, width=8)
        self.reservation_id_entry.pack()

        self.checkin_button1 = tk.Button(self.frame1, text="Επιλογή ID κράτησης", command=self.assign_loop)
        self.checkin_button1.pack()

        self.lvariable = tk.StringVar()
        self.checkin_listbox = tk.Listbox(self.frame1, listvariable=self.lvariable)
        self.checkin_listbox.pack()

        self.buttonpressed = tk.StringVar()  # wait for input
        self.checkin_button2 = tk.Button(self.frame1, text="Αντιστοίχιση δωματίου σε κράτηση",
                                         command=lambda: self.buttonpressed.set("yes"))
        self.checkin_button2.pack()

    def make_summary_tab(self):

        self.tab2 = tk.Frame(self.tabcontrol)
        self.frame2 = tk.Frame(self.tab2)
        self.frame2.pack(side="left")
        self.tabcontrol.add(self.tab2, text="Στατιστικά")

        self.from_month = tkcalendar.DateEntry(self.frame2, width=10, selectmode='day', date_pattern="yyyy-mm-dd")
        self.from_month.pack()
        self.to_month = tkcalendar.DateEntry(self.frame2, width=10, selectmode='day', date_pattern="yyyy-mm-dd")
        self.to_month.pack()

        self.stat_button = tk.Button(self.frame2, text="Επιλογή διαγράμματος", command=self.create_figures)
        self.stat_button.pack()

        self.canvas = tk.Canvas(self.frame2)
        self.canvas.pack()

    def create_figures(self, *args):
        for child in self.canvas.winfo_children():
            child.destroy()
        self.fig = Figure(figsize=(15, 5))
        self.f1 = self.fig.add_subplot(131)
        self.f1.title.set_text("Κρατήσεις")
        self.f2 = self.fig.add_subplot(132)
        self.f2.title.set_text("Κέρδη")
        self.f3 = self.fig.add_subplot(133)
        self.f3.title.set_text("Μέση διάρκεια παραμονής")

        self.bar = FigureCanvasTkAgg(self.fig, master=self.canvas)
        from_month = self.from_month.get_date()
        to_month = self.to_month.get_date()
        if from_month == to_month:
            step = "D"
            print(step)
        else:
            step = "M"
        x_axis = [i.strftime("%m/%Y") for i in
                  pd.date_range(start=from_month, end=to_month, freq=step, inclusive='both')]
        print(x_axis)
        # reservations
        reservations = []
        profits = []
        avg_period_of_stay = []
        for i in x_axis:
            self.cursor.execute("SELECT count(*),sum(total_price) FROM reservation WHERE strftime('%m',arrival_date)=?",
                                (i[0:2],))
            result = self.cursor.fetchone()
            reservations.append(result[0])
            profits.append(result[1])
            self.cursor.execute(
                "SELECT avg(julianday(departure_date)-julianday(arrival_date)) from reservation where strftime('%m',arrival_date)=?",
                (i[0:2],))
            avg_period_of_stay.append(self.cursor.fetchone()[0])
        print(reservations, profits, avg_period_of_stay)
        self.f1.plot(x_axis, reservations, 'bo-')
        self.f2.plot(x_axis, profits, 'bo-')
        self.f3.plot(x_axis, avg_period_of_stay, 'bo-')
        self.bar.draw()
        self.bar.get_tk_widget().pack()

    def assign_loop(self, *args):
        rnum = int(self.reservation_id_entry.get())
        checkquery = '''SELECT *
        FROM reservation as r
        WHERE r.reservation_num=? AND (SELECT sum(i.num_of_rooms)
            from includes as i where i.reservation_number=r.reservation_num) > (SELECT count(c.room_num) from checkin as c where c.reservation_num=r.reservation_num)'''
        self.cursor.execute(checkquery, (rnum,))
        if self.cursor.fetchone() == None:
            messagebox.showinfo(message="Το check in έχει ήδη καταχωρηθεί")
            return
        includesquery = "SELECT room_type_id,num_of_rooms FROM includes WHERE reservation_number=?"
        roomsquery = "SELECT r.room_num FROM room as r left join (checkin natural join reservation) as c " \
                     "on r.room_num=c.room_num " \
                     "WHERE room_type_id=? AND (reservation_num IS NULL OR ? > departure_date)"
        checkinquery = '''INSERT INTO checkin VALUES (?,?,?,?);'''
        self.cursor.execute(includesquery, (rnum,))  # get
        ids = dict(self.cursor.fetchall())
        for roomtypeid, num_of_rooms in ids.items():
            for _ in range(num_of_rooms):
                self.cursor.execute(roomsquery, (roomtypeid, datetime.date.today()))
                room_numbers = self.cursor.fetchall()
                self.lvariable.set(room_numbers)

                self.checkin_button2.wait_variable(self.buttonpressed)  # wait for admin to assign room
                # after button is pressed
                selected_room = self.checkin_listbox.get(self.checkin_listbox.curselection())[0]

                self.hoteldb.execute(checkinquery, (rnum, selected_room, self.adminid, datetime.datetime.today()))
                self.hoteldb.commit()
        self.lvariable.set('')
        messagebox.showinfo(message="Επιτυχής καταχώρηση check-in")

    def confirm_reservation(self, *args):
        arrival = self.arrival_entry.get_date()
        departure = self.departure_entry.get_date()
        ppl = int(self.num_of_ppl_entry.get())
        choice = int(self.optionvar.get()) - 1
        roomtype_ids = self.last_search_results[choice]

        customer = Customer(self.current_user)
        customer.make_reservation(self.hoteldb, self.cursor, arrival, departure, roomtype_ids, ppl)

        # reset everything
        self.arrival_entry.delete(0, tk.END)
        self.departure_entry.delete(0, tk.END)
        self.num_of_ppl_entry.delete(0, tk.END)
        for item in self.roomsView.get_children():
            self.roomsView.delete(item)
        self.last_search_results = []

    def refresh_departure_entry(self, event):
        self.departure_entry.delete(0, "end")
        self.departure_entry.config(mindate=self.arrival_entry.get_date() + datetime.timedelta(days=1))

    def get_room_results(self):
        arrival = self.arrival_entry.get_date()
        departure = self.departure_entry.get_date()
        ppl = int(self.num_of_ppl_entry.get())
        b = self.var1.get()
        p = self.var2.get()
        self.last_search_results = find_scenarios(self.hoteldb, self.cursor, arrival, departure, ppl, balcony=b, pets=p)
        if len(self.last_search_results) == 0:
            messagebox.showinfo(message="Δεν υπάρχουν διαθέσιμα δωμάτια")
            return
        # refresh optionmenu box
        self.options = [i + 1 for i, v in enumerate(self.last_search_results)]
        print(self.options)
        self.selector.set_menu(self.options[0], *self.options)

        # clear treeview
        for item in self.roomsView.get_children():
            self.roomsView.delete(item)

    def display_result(self, *args):
        if not self.last_search_results:
            return
        total_days = self.departure_entry.get_date() - self.arrival_entry.get_date()
        # clear treeview
        for item in self.roomsView.get_children():
            self.roomsView.delete(item)

        choice = int(self.optionvar.get()) - 1
        ids = self.last_search_results[choice]
        # print(ids)
        final_price = 0
        for id in ids:
            self.cursor.execute("SELECT * FROM room_type WHERE room_type_id=?", (id,))
            row = self.cursor.fetchone()
            total_room_price = row[-1] * total_days.days
            final_price += total_room_price
            # print(row)
            self.roomsView.insert('', tk.END, values=row + (total_room_price,))
        self.roomsView.insert('', tk.END, values=['', '', '', '', '', final_price])

    def get_userid(self, user):
        self.current_user = user

        self.make_search_tab()
        self.make_reservations_tab()
        self.state(newstate='normal')
        print("After login the userid is", self.current_user, self.current_user.userid)

    def get_adminid(self, user):
        self.current_user = user
        self.adminid = Admin(user).get_id(self.cursor)
        self.make_checkin_tab()
        self.make_summary_tab()
        self.state(newstate='normal')
        print("After login the userid is", self.current_user, self.current_user.userid, self.adminid)

    def display_reservations(self, *args):
        customer = Customer(self.current_user)
        id = customer.get_id(self.cursor)
        for item in self.roomsview2.get_children():
            self.roomsview2.delete(item)
        for item in self.resview.get_children():
            self.resview.delete(item)

        self.cursor.execute("SELECT * FROM reservation where customer_id=?", (id,))
        rows = self.cursor.fetchall()

        for reservation in rows:
            self.resview.insert("", tk.END, values=reservation)

    def display_res_details(self, *args):
        reservation = self.resview.focus()
        for item in self.roomsview2.get_children():
            self.roomsview2.delete(item)
        if reservation == '':
            messagebox.showinfo(message="Διάλεξε μία κράτηση")
        else:
            reservation_number = self.resview.item(reservation).get("values")[0]
            print("displayres", reservation_number)
            self.cursor.execute(
                "SELECT j.room_type_id,capacity,num_of_rooms FROM (includes join room_type rt on rt.room_type_id = includes.room_type_id) as j WHERE reservation_number=?",
                (reservation_number,))
            for row in self.cursor.fetchall():
                self.roomsview2.insert("", tk.END, values=row)

    def delete_reservation(self, *args):
        reservation = self.resview.focus()
        if reservation == '':
            messagebox.showinfo(message="Διάλεξε μία κράτηση")

        else:
            dialog = messagebox.askyesno(message="Σίγουρα θες να ακυρώσεις την κράτηση σου;")
            if dialog == "no":
                return
            else:
                reservation_num = self.resview.item(reservation).get("values")[0]
                print("delete", reservation_num)
                self.hoteldb.execute('''DELETE FROM reservation WHERE reservation_num=?''', (reservation_num,))
                self.display_reservations()

    def print_selection(self, *args):
        if (self.var1.get() == 1) & (self.var2.get() == 0):
            print('Θέλω μπαλκόνι')
        elif (self.var1.get() == 0) & (self.var2.get() == 1):
            print('Έχω κατοικίδιο')
        elif (self.var1.get() == 0) & (self.var2.get() == 0):
            print('Δεν έχω προτίμιση για μπαλκόνι ούτε κατοικίδιο')
        else:
            print('Θέλω και μπαλκόνι και κατοικίδιο')
            return
