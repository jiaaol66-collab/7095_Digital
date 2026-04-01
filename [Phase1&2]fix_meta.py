import os, shutil
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pyarrow.compute as pc
import pyarrow as pa
import time

t0 = time.time()

DATA_LAKE = r".\data_lake"

BRAND_SET_LOWER = {
    "apple", "samsung", "google", "sony", "oneplus", "xiaomi", "oppo", "huawei",
    "motorola", "nokia", "realme", "vivo", "zte", "blackberry", "honor",
    "dell", "hp", "lenovo", "asus", "acer", "microsoft", "razer", "msi",
    "toshiba", "gigabyte", "lg", "alienware", "system76",
    "bose", "jbl", "sennheiser", "jabra", "anker", "soundcore",
    "beats", "shure", "audio-technica", "skullcandy",
    "plantronics", "beyerdynamic", "marshall",
    "logitech", "corsair", "steelseries", "hyperx", "roccat",
    "zowie", "glorious", "ducky",
    "canon", "nikon", "fujifilm", "gopro",
    "panasonic", "olympus", "leica", "dji", "insta360", "sigma", "pentax",
    "tcl", "hisense", "vizio", "philips", "viewsonic", "benq", "aoc",
}

META_COLS = ["parent_asin", "title", "price", "store", "main_category",
             "average_rating", "rating_number", "details"]

for dataset_name, table_name in [("Electronics", "elec"), ("Cell_Phones_and_Accessories", "cellp")]:
    print(f"\n{'='*60}")
    print(f"🔄 [{dataset_name}]")

    meta_in  = os.path.join(DATA_LAKE, f"meta_{table_name}.parquet")
    meta_out = os.path.join(DATA_LAKE, f"{dataset_name}_meta_clean.parquet")
   
    # Delete the Spark legacy directory with the same name
    if os.path.exists(meta_out):
        shutil.rmtree(meta_out) if os.path.isdir(meta_out) else os.remove(meta_out)
        print(f"   🗑️  Cleared old: {meta_out}")

    dataset = ds.dataset(meta_in, format="parquet")
    writer  = None
    total   = 0

    for batch in dataset.to_batches(columns=META_COLS, batch_size=50000):
        store_col = pc.utf8_lower(batch.column("store"))
        mask      = pc.is_in(store_col, value_set=pa.array(list(BRAND_SET_LOWER)))
        filtered  = batch.filter(mask)
        if filtered.num_rows == 0:
            continue
        table = pa.Table.from_batches([filtered])
        if writer is None:
            writer = pq.ParquetWriter(meta_out, table.schema)
        writer.write_table(table)
        total += filtered.num_rows
        print(f"   ⏳ {total:,} rows...", end="\r")

    if writer:
        writer.close()
    print(f"\n   ✅ {total:,} rows → {dataset_name}_meta_clean.parquet  ({time.time()-t0:.1f}s)")

print("\n✨ Done!")