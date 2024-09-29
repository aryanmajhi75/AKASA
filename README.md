# AKASA
 
## Setup Instructions

> Note:  the instructions are based on my own system i.e., Ubuntu Linux 24.04 LTS, if you are using any other system then follow the instructions for that OS.
> 
- Install docker using cli, for ubuntu it works like this:

```bash
sudo apt-get update
sudo apt-get install ./docker-desktop-<arch>.deb
```

For installation guide for other OS, follow the documentation : https://docs.docker.com/engine/install/

- Pull mysql 8.1 image to docker

```bash
docker pull mysql:8.1
```

- Run docker image mysql 8.1 with credentials and port number

```bash
docker volume create akasa

docker volume inspect akasa

docker run -d \
-e MYSQL_ROOT_PASSWORD=1234 \
-e MYSQL_PASSWORD=1234 \
-e MYSQL_USER=aryan \
-e MYSQL_DATABASE=aviation_data \
-v mysql_volume:/var/lib/mysql \
-p 3306:3306 \
mysql:8.1
```

- Find the name of the image (last column), for my case it is called **funny_nobel**

```bash
docker ps
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/373d6c32-f869-4651-a36f-b16af7348a41/5a4c286e-f9a4-4622-8ba2-b077415ed108/image.png)

- Execute the docker image with the name of the image

```bash
docker exec -it funny_nobel mysql -uaryan -p
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/373d6c32-f869-4651-a36f-b16af7348a41/18e4191c-8c5d-43f4-806d-13853cae22a9/image.png)

- If the docker image was stopped, we need to start the image again for mysql to run.

```bash
docker start <image-name>
docker exec -it funny_nobel mysql -uaryan -p
```

- After mysql is setup, we need to make a table FlightSchedule and then fill the table.

```sql
// Create the table FlightSchedule
CREATE TABLE FlightSchedule (
    FlightNumber VARCHAR(10),
    DepartureDate VARCHAR(10),
    DepartureTime VARCHAR(8),
    ArrivalDate VARCHAR(10),
    ArrivalTime VARCHAR(8),
    Airline VARCHAR(50),
    DelayMinutes INT
);

// Insert data into the table
INSERT INTO FlightSchedule (FlightNumber, DepartureDate, DepartureTime, ArrivalDate, ArrivalTime, Airline, DelayMinutes)
VALUES
('AA1234', '09/01/2023', '08:30 AM', '09/01/2023', '10:45 AM', 'American Airlines', 15),
('DL5678', '09/01/2023', '01:15 PM', '09/01/2023', '03:30 PM', 'Delta', 5),
('UA9101', '09/01/2023', '05:00 PM', '09/01/2023', '07:15 PM', 'United Airlines', 25),
('AA1234', '09/01/2023', '08:30 AM', '09/01/2023', '10:45 PM', 'American Airlines', 30),
('DL5678', '09/02/2023', '02:00 PM', '09/02/2023', '04:10 PM', 'Delta', NULL),
('UA9101', '09/02/2023', '05:00 PM', '09/02/2023', '07:15 PM', 'United Airlines', 20),
('AA1234', '09/02/2023', '08:30 PM', '09/03/2023', '10:45 AM', 'American Airlines', 60),
('DL5678', '09/03/2023', '01:00 PM', '09/03/2023', '03:30 PM', 'Delta', 10),
('UA9101', '09/03/2023', '03:00 PM', '09/03/2023', '05:20 PM', 'United Airlines', NULL),
('AA1234', '09/03/2023', '08:30 AM', '09/03/2023', '10:00 AM', 'American Airlines', 15),
('DL5678', '09/04/2023', '12:30 PM', '09/04/2023', '02:40 PM', 'Delta', 25),
('UA9101', '09/04/2023', '07:00 PM', '09/04/2023', '09:15 PM', 'United Airlines', 45);

```

Since I’m using Ubuntu, the OS doesn’t recommend to install python packages to root, so I have an environment where the packages are saved

```bash
mkdir -p ~/.venvs
python3 -m venv ~/.venvs/<some-name>
~/.venvs/<some-name>/bin/python -m pip install <package-name>
```

The whole python script is running in a venv called **newenv**

```bash
python3 -m venv newenv
source newenv/bin/activate
```

To install any packages, we need to install it in the **newenv  and in the venvs**

```bash
~/.venvs/mysql/bin/python -m pip install <package-name>
pip install <package-name>
```

After the installations are done, we need to run the python script named **analytics.py** 

```bash
python3 analytics.py
```

After running all the graphs are stored in the same folder as png files and csv files for checking the changes in the dataset after every section - 1,2,3

The folder structure will be as follows:

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/373d6c32-f869-4651-a36f-b16af7348a41/8edc2444-1f85-476c-a9b1-6efcf8f1dce5/image.png)
