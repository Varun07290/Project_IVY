CREATE TABLE Criminals (
    Criminal_ID DECIMAL(6,0) NOT NULL,
    Last VARCHAR(15),
    First VARCHAR(10),
    Street VARCHAR(30),
    City VARCHAR(20),
    State CHAR(2),
    Zip CHAR(5),
    Phone CHAR(10),
    V_status CHAR(1) DEFAULT 'N',
    P_status CHAR(1) DEFAULT 'N',
    PRIMARY KEY (Criminal_ID)
);
-- Criminals V_status Y (Yes), N (No) 
-- Criminals P_status Y (Yes), N (No) 

CREATE TABLE Crimes (
    Crime_ID DECIMAL(9,0) NOT NULL ,
    Criminal_ID DECIMAL(6,0) NOT NULL,
    Classification CHAR(1) DEFAULT 'U',
    Date_charged DATE,
    Status CHAR(2) NOT NULL,
    Hearing_date DATE,
    Appeal_cut_date DATE,
    PRIMARY KEY (Crime_ID),
    FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID),
    CHECK (Hearing_date > Date_charged)
);
-- Crimes Classification F (Felony), M (Misdemeanor), O (Other), U (Undefined) 
-- Crimes Status CL (Closed), CA (Can Appeal), IA (In Appeal) 

CREATE TABLE Alias (
  Alias_ID DECIMAL(6,0) NOT NULL,
  Criminal_ID DECIMAL(6,0) NOT NULL,
  Alias VARCHAR(20),
  PRIMARY KEY (Alias_ID),
  FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID)
);

CREATE TABLE Prob_officer (
  Prob_ID DECIMAL(5,0) NOT NULL,
  Last VARCHAR(15),
  First VARCHAR(10),
  Street VARCHAR(30),
  City VARCHAR(20),
  State CHAR(2),
  Zip CHAR(5),
  Phone CHAR(10),
  Email VARCHAR(30),
  Status CHAR(1) NOT NULL,
  PRIMARY KEY (Prob_ID)
);
-- Prob_officers Status A (Active), I (Inactive) 


CREATE TABLE Sentences (
  Sentence_ID DECIMAL(6,0) NOT NULL,
  Criminal_ID DECIMAL(6,0) NOT NULL,
  Type CHAR(1),
  Prob_ID DECIMAL(5,0) NOT NULL,
  Start_date DATE,
  End_date DATE,
  Violations DECIMAL(3,0) NOT NULL,
  PRIMARY KEY (Sentence_ID),
  FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID),
  FOREIGN KEY (Prob_ID) REFERENCES Prob_officer(Prob_ID),
  CHECK (End_date >= Start_date)
);
-- Sentences Type J ( Jail Period), H (House Arrest), P (Probation) 


CREATE TABLE Crime_codes (
  Crime_code DECIMAL(3) NOT NULL,
  Code_description VARCHAR(30) NOT NULL UNIQUE,
  PRIMARY KEY (Crime_code)
);

CREATE TABLE Crime_charges (
  Charge_ID DECIMAL(10,0) NOT NULL,
  Crime_ID DECIMAL(9,0) NOT NULL,
  Crime_code DECIMAL(3,0) NOT NULL,
  Charge_status CHAR(2),
  Fine_amount DECIMAL(7, 2),
  Court_fee DECIMAL(7, 2),
  Amount_paid DECIMAL(7, 2),
  Pay_due_date DATE,
  PRIMARY KEY (Charge_ID),
  FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID),
  FOREIGN KEY (Crime_code) REFERENCES Crime_codes(Crime_code)
);

-- Crime_charges Charge_status PD (Pending), GL (Guilty), NG (Not Guilty) 

 
CREATE TABLE Officers (
  Officer_ID DECIMAL(8,0) NOT NULL,
  Last VARCHAR(15),
  First VARCHAR(10),
  Precinct CHAR(4) NOT NULL,
  Badge VARCHAR(14) UNIQUE,
  Phone CHAR(10),
  Status CHAR(1) DEFAULT 'A',
  PRIMARY KEY (Officer_ID)
);
-- Officers Status A (Active), I (Inactive) 

CREATE TABLE Crime_officers (
  Crime_ID DECIMAL(9,0) NOT NULL,
  Officer_ID DECIMAL(8,0) NOT NULL,
  PRIMARY KEY (Crime_ID, Officer_ID),
  Constraint crime_officers_fk1 FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID),
  Constraint crime_officers_fk2 FOREIGN KEY (Officer_ID) REFERENCES Officers(Officer_ID)
);


CREATE TABLE Appeals (
  Appeal_ID DECIMAL(5,0) NOT NULL,
  Crime_ID DECIMAL(9,0) NOT NULL,
  Filing_date DATE,
  Hearing_date DATE,
  Status CHAR(1) DEFAULT 'P',
  PRIMARY KEY (Appeal_ID),
  FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID)
);
-- Appeals Status P (Pending), A (Approved), D (Disapproved)


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    write_access BOOLEAN NOT NULL
);




-- Insert data
INSERT INTO Criminals (Criminal_ID, Last, First, Street, City, State, Zip, Phone, V_status, P_status) VALUES
(100001, 'Smith', 'John', '123 Oak St', 'Springfield', 'IL', '62704', '2175550123', 'Y', 'N'),
(100002, 'Johnson', 'Emily', '456 Maple Ave', 'Lincoln', 'NE', '68502', '4025550198', 'N', 'Y'),
(100003, 'Williams', 'David', '789 Pine Rd', 'Madison', 'WI', '53703', '6085550172', 'Y', 'Y'),
(100004, 'Brown', 'Sarah', '321 Birch Ln', 'Austin', 'TX', '73301', '5125550137', 'N', 'N'),
(100005, 'Jones', 'Michael', '654 Elm Dr', 'Reno', 'NV', '89501', '7755550189', 'Y', 'N'),
(100006, 'Garcia', 'Anna', '987 Cedar Blvd', 'Orlando', 'FL', '32801', '4075550164', 'N', 'Y'),
(100007, 'Miller', 'James', '246 Spruce St', 'Denver', 'CO', '80202', '3035550146', 'Y', 'N'),
(100008, 'Davis', 'Laura', '135 Oak Knoll Ter', 'Phoenix', 'AZ', '85001', '6025550195', 'N', 'N'),
(100009, 'Rodriguez', 'Robert', '864 Willow Way', 'Seattle', 'WA', '98101', '2065550173', 'Y', 'Y'),
(100010, 'Martinez', 'Linda', '432 Fir Ct', 'Atlanta', 'GA', '30301', '4045550110', 'N', 'Y');

INSERT INTO Crimes (Crime_ID, Criminal_ID, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date) VALUES
(100000001, 100001, 'F', '2021-05-10', 'CL', '2021-06-15', '2021-07-15'),
(100000002, 100002, 'M', '2022-01-20', 'CA', '2022-02-20', '2022-03-22'),
(100000003, 100003, 'O', '2020-12-05', 'IA', '2021-01-10', '2021-02-10'),
(100000004, 100004, 'F', '2022-03-15', 'CL', '2022-04-18', '2022-05-18'),
(100000005, 100005, 'M', '2021-07-22', 'CA', '2021-08-25', '2021-09-25'),
(100000006, 100006, 'F', '2020-11-30', 'IA', '2021-01-05', '2021-02-05'),
(100000007, 100007, 'O', '2022-02-14', 'CL', '2022-03-20', '2022-04-20'),
(100000008, 100008, 'M', '2021-08-11', 'CA', '2021-09-15', '2021-10-15'),
(100000009, 100009, 'F', '2020-09-09', 'IA', '2020-10-12', '2020-11-12'),
(100000010, 100010, 'M', '2022-04-05', 'CL', '2022-05-10', '2022-06-10');

INSERT INTO Alias (Alias_ID, Criminal_ID, Alias) VALUES
(100001, 100001, 'Shadow'),
(100002, 100002, 'Mystery'),
(100003, 100003, 'Ghost'),
(100004, 100004, 'Specter'),
(100005, 100005, 'Phantom'),
(100006, 100006, 'Rogue'),
(100007, 100007, 'Bandit'),
(100008, 100008, 'Vagabond'),
(100009, 100009, 'Nomad'),
(100010, 100010, 'Wanderer');

INSERT INTO Prob_officer (Prob_ID, Last, First, Street, City, State, Zip, Phone, Email, Status) VALUES
(10001, 'Harrison', 'Jane', '123 Main St', 'Anytown', 'NY', '10001', '2125550101', 'jane.harrison@email.com', 'A'),
(10002, 'Peters', 'John', '456 Center Rd', 'Springfield', 'IL', '62704', '2175550123', 'john.peters@email.com', 'I'),
(10003, 'Nguyen', 'Alice', '789 North Ave', 'Liberty', 'TX', '77575', '3465550198', 'alice.nguyen@email.com', 'A'),
(10004, 'Smith', 'Robert', '321 South St', 'Franklin', 'CA', '90001', '3105550137', 'robert.smith@email.com', 'A'),
(10005, 'Garcia', 'Maria', '654 West Blvd', 'Union', 'FL', '32003', '9045550189', 'maria.garcia@email.com', 'I'),
(10006, 'Brown', 'David', '987 East Ln', 'Harmony', 'NV', '89501', '7755550164', 'david.brown@email.com', 'A'),
(10007, 'Miller', 'Emma', '246 Maple Dr', 'Clarity', 'CO', '80014', '3035550146', 'emma.miller@email.com', 'I'),
(10008, 'Jones', 'William', '135 Pine Ct', 'Victory', 'AZ', '85001', '6025550195', 'william.jones@email.com', 'A'),
(10009, 'Davis', 'Sophia', '864 Birch Pl', 'Freedom', 'WA', '98101', '2065550173', 'sophia.davis@email.com', 'I'),
(10010, 'Martinez', 'Luis', '432 Oak Ter', 'Prosperity', 'GA', '30301', '4045550110', 'luis.martinez@email.com', 'A');

INSERT INTO Sentences (Sentence_ID, Criminal_ID, Type, Prob_ID, Start_date, End_date, Violations) VALUES
(100001, 100001, 'J', 10001, '2021-01-01', '2021-12-31', 301),
(100002, 100002, 'H', 10002, '2021-03-05', '2021-09-05', 202),
(100003, 100003, 'P', 10003, '2021-02-10', '2022-02-10', 101),
(100004, 100004, 'J', 10004, '2021-04-15', '2022-04-14', 511),
(100005, 100005, 'P', 10005, '2021-06-20', '2022-06-19', 321),
(100006, 100006, 'H', 10006, '2021-07-25', '2022-01-24', 112),
(100007, 100007, 'P', 10007, '2021-05-30', '2022-05-29', 232),
(100008, 100008, 'J', 10008, '2021-08-10', '2022-08-09', 734),
(100009, 100009, 'P', 10009, '2021-09-15', '2022-09-14', 465),
(100010, 100010, 'H', 10010, '2021-11-01', '2022-05-01', 265);



INSERT INTO Crime_codes (Crime_code, Code_description) VALUES
(101, 'Petty Theft'),
(102, 'Armed Robbery'),
(103, 'Vandalism'),
(104, 'Drug Possession'),
(105, 'Burglary'),
(106, 'Assault'),
(107, 'Identity Theft'),
(108, 'Fraud'),
(109, 'Public Intoxication'),
(110, 'Trespassing');


INSERT INTO Crime_charges (Charge_ID, Crime_ID, Crime_code, Charge_status, Fine_amount, Court_fee, Amount_paid, Pay_due_date) VALUES
(1000000001, 100000001, 101, 'PD', 500.00, 100.00, 600.00, '2022-01-15'),
(1000000002, 100000002, 102, 'GL', 1500.00, 300.00, 1800.00, '2022-02-20'),
(1000000003, 100000003, 103, 'NG', 200.00, 50.00, 250.00, '2022-03-10'),
(1000000004, 100000004, 104, 'PD', 1000.00, 200.00, 1200.00, '2022-04-05'),
(1000000005, 100000005, 105, 'GL', 1200.00, 250.00, 1450.00, '2022-05-18'),
(1000000006, 100000006, 106, 'NG', 800.00, 150.00, 950.00, '2022-06-12'),
(1000000007, 100000007, 107, 'PD', 700.00, 140.00, 840.00, '2022-07-09'),
(1000000008, 100000008, 108, 'GL', 1500.00, 300.00, 1800.00, '2022-08-15'),
(1000000009, 100000009, 109, 'NG', 300.00, 60.00, 360.00, '2022-09-20'),
(1000000010, 100000010, 110, 'PD', 400.00, 80.00, 480.00, '2022-10-25');

INSERT INTO Officers (Officer_ID, Last, First, Precinct, Badge, Phone, Status) VALUES
(10000001, 'Smith', 'John', 'P001', 'Bdg0012345', '2125550101', 'A'),
(10000002, 'Johnson', 'Emily', 'P002', 'Bdg0023456', '3125550123', 'I'),
(10000003, 'Williams', 'David', 'P003', 'Bdg0034567', '2135550135', 'A'),
(10000004, 'Brown', 'Sarah', 'P004', 'Bdg0045678', '4155550147', 'A'),
(10000005, 'Jones', 'Michael', 'P005', 'Bdg0056789', '3055550159', 'I'),
(10000006, 'Garcia', 'Anna', 'P006', 'Bdg0067890', '7025550161', 'A'),
(10000007, 'Miller', 'James', 'P007', 'Bdg0078901', '5035550173', 'A'),
(10000008, 'Davis', 'Laura', 'P008', 'Bdg0089012', '4045550185', 'I'),
(10000009, 'Rodriguez', 'Robert', 'P009', 'Bdg0090123', '6175550197', 'A'),
(10000010, 'Martinez', 'Linda', 'P010', 'Bdg0101234', '7185550209', 'A');



INSERT INTO Crime_officers (Crime_ID, Officer_ID) VALUES
(100000001, 10000001),
(100000002, 10000002),
(100000003, 10000003),
(100000004, 10000004),
(100000005, 10000005),
(100000006, 10000006),
(100000007, 10000007),
(100000008, 10000008),
(100000009, 10000009),
(100000010, 10000010);


INSERT INTO Appeals (Appeal_ID, Crime_ID, Filing_date, Hearing_date, Status) VALUES
(10001, 100000001, '2022-01-10', '2022-04-15', 'P'),
(10002, 100000002, '2022-02-14', '2022-05-20', 'A'),
(10003, 100000003, '2022-03-19', '2022-06-25', 'D'),
(10004, 100000004, '2022-04-23', '2022-07-30', 'P'),
(10005, 100000005, '2022-05-28', '2022-09-05', 'A'),
(10006, 100000006, '2022-07-02', '2022-10-10', 'D'),
(10007, 100000007, '2022-08-06', '2022-11-15', 'P'),
(10008, 100000008, '2022-09-10', '2023-01-20', 'A'),
(10009, 100000009, '2022-10-15', '2023-02-25', 'D'),
(10010, 100000010, '2022-11-19', '2023-04-01', 'P');

INSERT INTO Login_Info (UserName, Password, Write_Access) VALUES
('user1', 'password1', FALSE),
('user2', 'password2', FALSE),
('user3', 'password3', FALSE),
('user4', 'password4', FALSE),
('user5', 'password5', FALSE),
('user6', 'password6', FALSE),
('user7', 'password7', FALSE),
('user8', 'password8', FALSE),
('user9', 'password9', FALSE),
('admin', 'adminpass', TRUE);
