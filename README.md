# COMP7095 Big Data Management: E-Commerce User Behavior Analysis

## System Setup

Our project requires Docker Desktop.

Once downloaded, type (or copy and paste) the following command in the terminal:

```bash
docker-compose up -d
```

Once the command is executed, type the following command in the terminal to get the token:

### Alternative
Run (copy and paste) the following command in a terminal to generate a token, then paste it into the link below.

[http://127.0.0.1:8888/lab?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX](http://127.0.0.1:8888/lab?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)

```bash
docker exec jupyter_analytics jupyter server list
```

### Recommended
Run the above command, copy the output link NOT INCLUDING **:: //home/jovyan**. 

Go to your notebook and click **Select Kernel** in the top-right corner.

Go to **Select Another Kernel...** > **Existing Jupyter Server...** and paste **output link** and replace the number and letter combination after the http:// with **localhost** in the input box.

e.g. http://5ab7977b7ef1:8888/?token=28737xxxxxxxxxxxxxxxxxxxxxxxxxxxxcf55d5 

➡️ http://localhost:8888/?token=28737xxxxxxxxxxxxxxxxxxxxxxxxxxxxcf55d5

Hit Enter, then Enter again... and you're in!

🚨 AND DO **NOT** FORGET to run the **First cell** before you do anything else!


## Team Roles & Pipeline Responsibilities

### Member 1: Data Ingestion & Preprocessing (Phase 1 & 2)
*Primary workspace: `[Phase1&2]_PreProcess.ipynb`*

* **Environment & Connector Initialization:** Bootstraps Spark sessions, local workspaces, MongoDB connector JARs, and HDFS checkpoint directories.
* **Storage Cleanup:** Automates HDFS directory tree validation/deletion and drops MongoDB databases to ensure a clean, reproducible state for every pipeline execution.
* **Dual-Track Data Ingestion:** Performs batch insertions of local JSONL files (metadata and reviews) into MongoDB using `insert_many` with dynamic progress tracking.
* **Pre-filtering & Data Lake Alignment:** Extracts metadata from MongoDB, applies brand whitelisting, executes schema casting, and aligns review data using the `parent_asin` key. Partitions and writes the synchronized data into HDFS (`/ecommerce/data_lake/meta` and `/review`) with optional local backup support.
* **Execution Mode Control:** Implements configuration flags to seamlessly toggle downstream Phase 3 & 4 reads between local Parquet files and the HDFS cluster.

### Member 2: Data Quality Assurance & Cleaning (Phase 3 & 4)
*Primary workspace: `[Phase3&4]_Storage&Analytics.ipynb`*

* **Metadata Cleansing:** Ingests raw data from the data lake and systematically handles null/invalid values, formats pricing fields, and identifies/removes price outliers using the Interquartile Range (IQR) method.
* **Review Cleansing:** Validates rating ranges, handles missing values in critical fields, trims `reviewText` whitespace, and deduplicates records based on a composite key `(reviewerID, asin, unixReviewTime)`. Generates comprehensive data quality statistics.
* **Clean Layer Generation:** Outputs the refined, production-ready datasets to a "clean layer" (`/ecommerce/data_lake/clean/meta` and `/review`) for downstream modeling.

### Member 3: Clustering & Business Analytics (Phase 3 & 4)
*Primary workspace: `[Phase3&4]_Storage&Analytics.ipynb`*

* **Dual-Feature Category Clustering:** Engineers multi-dimensional features for clustering:
    * *Textual:* Cleans titles, tokenizes text, filters custom brand stopwords, and applies Word2Vec.
    * *Structural:* Generates CountVectorizer features from product detail keys.
    * *Numerical:* Extracts capacity/size metrics and standardizes them via MinMaxScaler.
    * Fuses features using a Normalizer and applies K-Means clustering (using dynamic K-values tailored per category), appending the results to the clustered metadata.
* **Semantic Labeling & Probes:** Utilizes PySpark window functions to rank clusters by average price within categories, dynamically generating "tier labels" and employing noise-word probes for cluster validation.
* **Advanced Business Analytics:** Calculates premium metrics by comparing cluster baselines against store averages. Constructs indices for brand equity and cost-effectiveness, exporting the datasets for visual analytics.

### Member 4: Machine Learning Engineering (Phase 3 & 4)
*Primary workspace: `[Phase3&4]_Storage&Analytics.ipynb`*

* **Data Fusion:** Broadcast-joins store, price, and cluster attributes from the metadata to the review dataset. Constructs sentiment classification labels (ratings >= 4 defined as positive) to build the modeling dataset.
* **Model Training & Analysis:** Architects a Spark ML Pipeline (`Tokenizer` -> `StopWords` -> `TF-IDF` -> `Logistic Regression`) for sentiment prediction. Extracts deep insights, including store-level sentiment performance and price-bucket inflection points, and exports the findings.

### Member 5: Visualization & Dashboarding (Phase 3 & 4)
*Primary workspace: `[Phase3&4]_Storage&Analytics.ipynb`*

* **Visual Analytics:** Consumes upstream CSV exports (premiums, sentiment analysis, inflection points) to generate multi-dimensional charts (bar, scatter, and line graphs). Selects key clusters based on data variance and business value, rendering and saving the final PNG assets for the project presentation and report.

---

## Overall Delivery Pipeline

* **Member 1:** Raw Data -> MongoDB / HDFS Data Lake *(Ingestion)*
* **Member 2:** Data Lake -> Clean Layer *(Quality Assurance)*
* **Member 3:** Clean Layer -> Clustering Results & Brand Analytics Datasets *(Feature Engineering & Business Logic)*
* **Member 4:** Clustering Results + Reviews -> Sentiment Model & Insight Datasets *(Machine Learning)*
* **Member 5:** Upstream Data Exports -> Final Charts & Visual Deliverables *(Reporting)*
