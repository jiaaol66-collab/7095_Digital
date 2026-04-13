# COMP7095 Big Data Management: E-Commerce User Behavior Analysis

## System Setup

Our project requires Docker Desktop.

Once downloaded, launch it,

❗Attention❗:
For \[Phase1&2] and \[Phase3&4], please uncomment or comment out first module in docker-compose.yml,
For detail, please refer the specific notebook.

Type (or copy and paste) the following command in the terminal:

```bash
docker-compose up -d
```

Once the command is executed, type the following command in the terminal to get the token:

### Alternative

Run (copy and paste) the following command in a terminal to generate a token, then paste it into the link below.

<http://127.0.0.1:8888/lab?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX>

```bash
docker exec jupyter_analytics jupyter server list
```

### Recommended

Run the above command, copy the output link NOT INCLUDING **:: //home/jovyan**.

Go to your notebook and click **Select Kernel** in the top-right corner.

Go to **Select Another Kernel...** > **Existing Jupyter Server...** and paste **output link** and replace the number and letter combination after the http\:// with **localhost** in the input box.

e.g. <http://5ab7977b7ef1:8888/?token=28737xxxxxxxxxxxxxxxxxxxxxxxxxxxxcf55d5>

➡️ <http://localhost:8888/?token=28737xxxxxxxxxxxxxxxxxxxxxxxxxxxxcf55d5>

Hit Enter, then Enter again... and you're in!

🚨 AND DO **NOT** FORGET to run the **Spark Session Init Cell** before you do anything else!

## Docker

| **Service Component** | **Internal Reference** | **Accessible Endpoint**   | **Description**                                                    |
| :-------------------- | :--------------------- | :------------------------ | :----------------------------------------------------------------- |
| **HDFS NameNode**     | namenode               | <http://localhost:9870>   | Web UI for monitoring the Hadoop Distributed File System (HDFS).   |
| **HDFS DataNode**     | datanode               | N/A                       | The actual storage of HDFS data blocks.                            |
| **Spark Master**      | spark\_master          | <http://localhost:8080>   | Central cluster manager UI for Apache Spark.                       |
| **Spark Worker**      | spark\_worker          | spark://spark-master:7077 | Worker node execution environment.                                 |
| **JupyterLab**        | jupyter\_analytics     | <http://localhost:8888>   | PySpark interactive notebook environment.                          |
| **MongoDB**           | mongodb                | mongodb://mongodb:27017/  | Staging database / Initial ingestion layer (for Phase 1 & 2 only). |

## Test Data

We provide a small test dataset for you to try out the pipeline.
The test data is available in the `data_test` directory.
Please set the \[Phase1&2] notebook **Test Mode Cell** to True.

## Execution Workflow (Notebook Execution Order)

The reproducible experiments in this project are conducted through two sequential Jupyter Notebooks. To ensure consistent results, it is highly recommended to execute the workflow strictly in the following order: environment deployment, data lake population, data cleansing, clustering, and final analytics & visualization.

### Step 0: Environment Initialization

*(Please see the System Setup deployment instructions.)*

### Step 1 — Phase 1 & 2: Data Collection and Preprocessing (Member 1)

**Target Notebook:** `[Phase1&2]_PreProcess.ipynb`

Execute the cells sequentially as follows:

1. **Spark Session Initialization (Prerequisite):** Configures the Spark environment (`fs.defaultFS=hdfs://namenode:9000`), checkpoint directories, and required dependencies.
2. **Optional Environment Cleanup:** Clears existing HDFS directories (`/ecommerce`) and drops the MongoDB collection (`amazon_reviews`) to ensure a fresh, interference-free execution.
3. **Raw JSONL Ingestion to MongoDB:** Performs bulk ingestion of all `data/meta/*.jsonl` and `data/review/*.jsonl` files into MongoDB, driven by the dataset configuration in `configs/datasets.txt`.
4. **MongoDB to HDFS Migration with Alignment:** Extracts metadata from MongoDB, applying brand whitelists and schema casting.
5. **Identifier Compilation:** Compiles a set of valid `parent_asin` identifiers.
6. **Review Filtering:** Filters the review dataset using this set to guarantee strict alignment between reviews and metadata.
7. **Data Lake Storage:** Writes the aligned datasets to the HDFS Data Lake as Parquet files (`hdfs://namenode:9000/ecommerce/data_lake/meta/{table_name}` and `/review/{table_name}`).

> **Reproducibility & Collaborative Handover Flags:**
> The pipeline employs `CREATEFILE` and `configs/local` markers to control data reading and writing at various levels. To support teamwork, the `CREATEFILE` switch allows team members to export processed data to local artifacts and share specific data states via Google Drive during handovers. This ensures the subsequent team member can pick up the pipeline with the exact outputs from the previous stage. While this eases collaborative workflows, please note that for final runs to ensure bit-identical results across different environments, **HDFS mode should still be used predominantly**.

***

### Step 2 — Phase 3 & 4: Storage, Cleansing, Clustering, and Analytics

**Target Notebook:** `[Phase3&4]_Storage&Analytics.ipynb`

Implement the cells in a serial manner:

1. **Spark Session Startup (Prerequisite):** Starts the Spark setting (`fs.defaultFS=hdfs://namenode:9000`), checkpoint directories, and dependencies.
2. **Optional HDFS Wipe:** Hard reset cell that can be used to delete `/ecommerce` (only run when a complete rerun of the pipeline is required).
3. **Local Data Synchronization:** Copies `data_lake/*.parquet` artifacts to HDFS, when necessary (not executed in the presence of the `configs/local` flag).
4. **Raw Data Preview/Schema Check:** Checks the readability of the HDFS raw paths and displays the schema/sample rows to verify input integrity.
5. **Data Cleansing (Member 2: Data Quality Engineer):** Loads raw metadata and reviews.
   - Performs price casting, invalid price filtering, IQR-based outlier removal, and review text deduplication cleansing.
   - Writes the clean layer to `/ecommerce/data_lake/clean/meta` and `/clean/review`.
   - Calculates pre- and post-row counts to give an auditing trail of data volume variations.
6. **Output Validation Tests:** Confirms the existence of output paths, checks for empty output paths, and satisfies critical constraints (setting a baseline of reproducibility).
7. **Category-Aware Clustering (Member 3):** Reads clean metadata and clusters data by main-category.
   - Constructs features and performs clustering using fixed random seeds (e.g., `seed=42`).
   - Writes metadata (partitioned by cluster) back to HDFS.
   - **Review Filtering & Cluster Merging:** Constructs a `parent_asin` to cluster mapping, broadcasts a join with clean reviews, and stores the reviews in HDFS.
8. **Premium & Positioning Analytics (Member 3):** Calculates cluster baselines and store premium measures using clustered metadata, and writes the resulting CSVs to local artifact directory (`/home/jovyan/work/data_lake/`).
9. **Sentiment Pipeline (Member 4):** Fuses preview and metadata operations to run the sentiment analysis pipeline, exporting insight tables in the form of CSV to the local artifact directory.
10. **Data Visualization (Member 5):** Processes the resulting CSVs to create Seaborn dashboards, and stores them as PNGs to be used in Section 4 of the report.

***

## Result Checking (CSV and Seaborn Outputs)

At the end of the above workflow, the generated artifacts will be stable and appear in the mounted directory of the container. These artifacts are firmly consistent with the results provided in Section 4 of the report.

### A. Expected CSV Outputs (Section 4 Table Inputs)

All analytical CSVs are exported to `/home/jovyan/work/data_lake/`. Key outputs include:

**Brand Premium & Positioning:**

- `data_lake/Micro-brand-premium-index.csv` (Micro-level metrics)
- `data_lake/Macro_brand_premium.csv` (Cross category macro summary)

**Sentiment Insight Tables:**

- `data_lake/store-sentiment.csv` (Store-level aggregation)
- `data_lake/price-sentiment.csv` (Price-bucket inflection inputs)

> **Verification Checklist:** Repeat runs on the same artifact and source data will produce the same file structures, column schemas, and rows, and will be totally reproducible analytically.

### B. Visualization (Section 4 Figures)

Visualizations are created using the Member 5 module and saved as PNGs (directly based on the CSVs above):

- `pngs/M5/M3_macro_final_combined.png`
- `pngs/M5/M3_micro_cluster_price.png`
- `pngs/M5/M4_price_sentiment.png`
- `pngs/M5/M4_store_sentiment.png`

> **Checklist Verification:** Since these visualizations are data-driven, the ability to recreate the CSV results is a guarantee that all charts (premium, sentiment, and inflection points) discussed in Section 4 can be recreated deterministically.

### C. Determinism and Reproducibility Guarantees

- **Algorithmic Stability:** Hardcoded critical random seeds (`seed=42`) have been explicitly encoded in the clustering (KMeans), embedding (Word2Vec), and data splitting (`randomSplit`) modules in the notebook to avoid execution variation.
- **Environmental Consistency:** It is ensured that full reproducibility is achieved using the given Docker Compose environment, the same source of HDFS data lake, and following the same sequence of Phase 1 to Phase 4 execution.

***

## Execution Performance & Quick Verification Mode

To establish a transparent performance baseline and facilitate efficient evaluation, we have documented the total execution times for both the full-scale dataset and a provided test dataset.

### Baseline Execution Times

The following table summarizes the runtime required to execute the complete pipeline on our containerized environment. *(Note: 5589.89 seconds is approximately 1.5 hours).*

| Pipeline Stage  | Full Dataset Runtime | Test Dataset Runtime |
| :-------------- | :------------------- | :------------------- |
| **Phase 1 & 2** | 5589.89 seconds      | 89.34 seconds        |
| **Phase 3 & 4** | 706.67 seconds       | 131.36 seconds       |

