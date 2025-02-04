# Data Warehouse for Ethiopian Medical Business Data

## Overview

This project aims to build a comprehensive **data warehouse** for Ethiopian medical business data scraped from various Telegram channels. The data collected includes information about medical products, services, and health-related news. The project includes several stages: data scraping, image detection using YOLO (You Only Look Once), data transformation using DBT (Data Build Tool), and exposing the data via a REST API using FastAPI.

The primary goal of this project is to collect, clean, transform, and organize the data efficiently in a data warehouse, making it accessible via a RESTful API for use in further analysis, decision-making, or integration with other applications.

---

## Installation

### 1. Clone the Repository

Clone the repository to your local machine.

### 2. Set up a Virtual Environment

Create and activate a virtual environment.

### 3. Install Dependencies

Install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

Set up your PostgreSQL database and configure the `database.py` file with your database credentials. The database schema will be automatically created when you run the project.

---

## Project Components

### 1. **Data Scraping**

Data is scraped from several Telegram channels that provide medical-related messages, images, and other media. These channels include `DoctorsET`, `Chemed`, `lobelia4cosmetics`, `yetenaweg`, and `EAHCI`. The scraping is powered by the **Telethon** library.

### 2. **Image Detection Using YOLO**

YOLO (You Only Look Once) is used to perform **object detection** on images scraped from the Telegram channels. This model detects medical-related objects in images, such as medical products and equipment. The detection results, including confidence scores and bounding box coordinates, are saved in the database.

### 3. **Data Transformation Using DBT**

DBT (Data Build Tool) is used to clean and transform the raw data. The raw data is normalized, cleaned, and validated, ensuring its integrity for analysis. DBT models define how the data should be transformed, allowing for easy management and reproducibility.

### 4. **Database Models and CRUD Operations**

SQLAlchemy is used to configure the database connection. The data models, defined using **SQLAlchemy**, represent the tables in the database. CRUD (Create, Read, Update, Delete) operations are implemented for interacting with the data, including adding new detections and retrieving data.

### 5. **FastAPI REST API**

A **FastAPI** application is built to expose the data via a RESTful API. This API allows users to interact with the data, such as creating new YOLO detections, fetching detections, and retrieving specific entries.

---

## API Endpoints

- **POST /detections/**: Create a new YOLO detection entry.
- **GET /detections/**: Fetch a list of YOLO detections with pagination.
- **GET /detections/{detection_id}**: Fetch a specific YOLO detection entry by its ID.

---

## Testing the API

You can test the API using **Postman** or **Curl**. Example requests are provided in the documentation to interact with the API and verify the functionality.

---

## Future Improvements

- **Expand the Dataset**: Collect more images and data from additional Telegram channels to improve the YOLO model’s performance.
- **Scalability**: Migrate to a cloud-based database (e.g., Amazon RDS, Google BigQuery) for better scalability as the dataset grows.
- **Advanced API Features**: Add more advanced querying capabilities to the FastAPI application, such as filtering detections based on object type or confidence score.
- **Security**: Implement authentication and authorization mechanisms to secure the API.

---

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. Any improvements, bug fixes, or new features are welcome!

---

## License

This project is open source and available under the MIT License.

---

## Contact

For any questions or inquiries, please reach out to the project maintainers at:

- **GitHub**: [https://github.com/b-sam16/data-warehouse-project](https://github.com/your-username/data-warehouse-project)

---

## Acknowledgments

- **Telethon**: For scraping data from Telegram.
- **YOLO**: For object detection in images.
- **FastAPI**: For building the REST API.
- **DBT**: For data transformation. 

