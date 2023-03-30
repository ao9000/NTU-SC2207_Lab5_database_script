import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv


def establish_connection():
    load_dotenv()
    conn = pyodbc.connect('DRIVER={SQL Server};'
                          f'Server={os.getenv("SERVER_IP")};'
                          f'port={os.getenv("SERVER_PORT")};'
                          f'Database={os.getenv("DATABASE_NAME")};'
                          f'uid={os.getenv("DATABASE_USERNAME")};'
                          f'pwd={os.getenv("DATABASE_PASSWORD")};')
    cursor = conn.cursor()
    return cursor


def insert_data(cursor, df):
    print(f'Inserting data into {df.name} table')
    # Insert a dataframe into the database as records
    query = f'insert into {df.name} ({",".join(str(x) for x in df.columns.values)}) VALUES ({",".join("?" for x in df.columns.values)})'
    data = [row for row in df.itertuples(index=False, name=None)]
    print(query)
    print(data)
    try:
        cursor.executemany(query, data)
    except pyodbc.IntegrityError as e:
        print(f'Record already exists')
        print(e)
        cursor.rollback()
        return
    cursor.commit()


def load_data_from_csv():
    df_dict = {}

    path = 'tables'
    for file in os.listdir(path):
        print(f"Loading csf file: {file}")
        if file.endswith('.csv'):
            data = pd.read_csv(f'{path}/{file}')
            df = pd.DataFrame(data)
            df.name = file.split('.')[0]
            df_dict[df.name] = df

    return df_dict


def print_table(cursor, table_name):
    cursor.execute(f'''SELECT * FROM {table_name}''')
    for row in cursor:
        print(row)


# All Operations
def delete_all_records(cursor, table_name):
    cursor.execute(f'''DELETE FROM {table_name}''')
    cursor.commit()


def insert_all_data(cursor, df_dict):

    for value in [df_dict['employees'], df_dict['customers'], df_dict['bookstore'], df_dict['publication'],
                  df_dict['magazines'], df_dict['books'], df_dict['orders'], df_dict['complaints'],
                  df_dict['complaints_on_bookstore'], df_dict['complaints_on_orders'], df_dict['complaint_status'],
                  df_dict['stocks_in_bookstore'], df_dict['price_history'], df_dict['items_in_orders'], df_dict['items_order_status']]:
        insert_data(cursor, value)


def delete_all_data_from_all_tables(df_list, cursor):
    for key in df_list.keys():
        delete_all_records(cursor, key)


def print_all_tables(df_list, cursor):
    for key in df_list.keys():
        print_table(cursor, key)


def drop_all_tables(df_dict, cursor):
    for key in df_dict.keys():
        print(f'Dropping table: {key}')
        try:
            cursor.execute(f'DROP TABLE {os.getenv("database_name")}.dbo.{key}')
        except pyodbc.ProgrammingError:
            print(f'Table: {key} does not exist')
            cursor.rollback()
            continue
        cursor.commit()


def create_all_tables(cursor):
    # Create all the main tables first

    # Employees
    cursor.execute('''
CREATE TABLE employees(
	EID varchar(5),  
	Name varchar(50),
	salary int, 
	Primary Key(EID),
);
                   ''')
    cursor.commit()

    # Customers
    cursor.execute('''
CREATE TABLE customers(
	CID varchar(5), 
	Name varchar(50),
	PRIMARY KEY(CID)
);
                                               ''')
    cursor.commit()

    # Bookstore
    cursor.execute('''
CREATE TABLE bookstore(
	BID varchar(5)
	PRIMARY KEY (BID)
);
                                                                       ''')
    cursor.commit()

    # Publication
    cursor.execute('''
CREATE TABLE publication(
 	PubID varchar(5), 
	publisher varchar(40),
 	year int, 
	PRIMARY KEY(PubID)
);
                                                       ''')
    cursor.commit()

    # Magazines
    cursor.execute('''
CREATE TABLE magazines(
	PubID varchar(5),
	issue varchar(20),
	title varchar(50),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),
);
                                                               ''')
    cursor.commit()

    # Books
    cursor.execute('''
CREATE TABLE books(
	PubID varchar(5),
	title varchar(50),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),
);
                                                           ''')
    cursor.commit()

    # Orders
    cursor.execute('''
CREATE TABLE orders
(
 	OrderID varchar(5) NOT NULL,
	date_time datetime NOT NULL,
	shipping_address varchar(20) NOT NULL,
    CID varchar(5) NOT NULL,
 	PRIMARY KEY(OrderID),
 	FOREIGN KEY (CID) REFERENCES customers(CID),
);
                                       ''')
    cursor.commit()

    # Complaints
    cursor.execute('''
CREATE TABLE complaints(
    	complaintID varchar(5) NOT NULL,
 	EID varchar(5) NOT NULL,
 	CID varchar(5) NOT NULL,
 	filed_date_time datetime NOT NULL,
 	Text varchar(100) NOT NULL,
 	handled_date_time datetime NOT NULL,
 	PRIMARY KEY(complaintID),
	FOREIGN KEY (EID) REFERENCES employees(EID),
	FOREIGN KEY (CID) REFERENCES customers(CID),
);
                   ''')
    cursor.commit()

    # Complaints on bookstore
    cursor.execute('''
CREATE TABLE complaints_on_bookstore(
	complaintID varchar(5),
	BID varchar(5),
	PRIMARY KEY (complaintID, BID),
	FOREIGN KEY (complaintID) REFERENCES complaints(complaintID),
	FOREIGN KEY (BID) REFERENCES bookstore(BID),
);
                       ''')
    cursor.commit()

    # Complaints on orders
    cursor.execute('''
CREATE TABLE complaints_on_orders(
	complaintID varchar(5),
	orderID varchar(5),
	PRIMARY KEY (complaintID, orderID),
	FOREIGN KEY (complaintID) REFERENCES complaints(complaintID),
	FOREIGN KEY (orderID) REFERENCES orders(orderID),
);

                           ''')
    cursor.commit()

    # Complaint status
    cursor.execute('''
CREATE TABLE complaint_status(
	date date,	
	complaintID varchar(5),
	state varchar(15),
	PRIMARY KEY (date, complaintID),
	FOREIGN KEY (complaintID) REFERENCES complaints(complaintID),
);
                               ''')
    cursor.commit()

    # Stocks in bookstore
    cursor.execute('''
CREATE TABLE stocks_in_bookstore(
	stockID varchar(5) NOT NULL,	
	BID varchar(5) NOT NULL,
	PubID varchar(5) NOT NULL,
	stock_qty int NOT NULL,
	stock_price DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (stockID),
	FOREIGN KEY (BID) REFERENCES bookstore(BID),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),
);
                                                                   ''')
    cursor.commit()

    # Price history
    cursor.execute('''
CREATE TABLE price_history(
	stockID varchar(5) NOT NULL,	
	BID varchar(5) NOT NULL,
	PubID varchar(5) NOT NULL,
	start_date date NOT NULL,
	end_date date,
	price DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (BID,stockID,PubID,start_date,end_date,price),
	FOREIGN KEY (stockID) REFERENCES stocks_in_bookstore(stockID),
	FOREIGN KEY (BID) REFERENCES bookstore(BID),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),	
);
                                                                           ''')
    cursor.commit()

    # Items in orders
    cursor.execute('''
CREATE TABLE items_in_orders(
	itemID varchar(5),
	BID varchar(5),
	stockID varchar(5),
	PubID varchar(5),
	orderID varchar(5),
	item_price decimal(5,2),
	item_qty int,
	Delivery_date date,
	Comment varchar(100),
	Rating int,
	Date_time datetime,
	CID varchar(5),
	PRIMARY KEY (itemID),
	FOREIGN KEY (CID) REFERENCES customers(CID),
	FOREIGN KEY (BID) REFERENCES bookstore(BID),
	FOREIGN KEY (stockID) REFERENCES stocks_in_bookstore(stockID),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),
	FOREIGN KEY (orderID) REFERENCES orders(orderID),
);
                                               ''')
    cursor.commit()

    # Item order status
    cursor.execute('''
CREATE TABLE items_order_status (
	date date,
	itemID varchar(5),
	stockID varchar(5),
	BID varchar(5),
	PubID varchar(5),
	state varchar(15),
	PRIMARY KEY (date,itemID,stockID,BID,PubID),
	FOREIGN KEY (itemID) REFERENCES items_in_orders(itemID),
	FOREIGN KEY (stockID) REFERENCES stocks_in_bookstore(stockID),
	FOREIGN KEY (BID) REFERENCES bookstore(BID),
	FOREIGN KEY (PubID) REFERENCES publication(PubID),	
);

                                           ''')
    cursor.commit()


def main():
    # Establish connection with SQL server
    cursor = establish_connection()
    while True:
        print("1. Drop all tables")
        print("2. Create all tables")
        print("3. Insert all data")

        choice = input("Enter Choice: ")
        match choice:
            case '1':
                # Load/refresh data from csv files
                df_dict = load_data_from_csv()

                drop_all_tables(df_dict, cursor)
            case '2':
                create_all_tables(cursor)
            case '3':
                # Load/refresh data from csv files
                df_dict = load_data_from_csv()

                insert_all_data(cursor, df_dict)


if __name__ == '__main__':
    main()
