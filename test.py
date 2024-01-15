# import os
# from datetime import datetime
# asins = ["jdksnsdjn", "jajaskjs", "jkasjsjkas", "kdjdjksdj"]
# print(datetime.now())
# # File path
# file_path = "textfile.txt"

# # Check if file exists. If not, create it.
# if not os.path.exists(file_path):
#     open(file_path, 'a').close()

# in_text_file = []
# with open(file_path, "r") as file:
#     in_text_file = file.readlines()

# in_text_file = [text_el.strip() for text_el in in_text_file]

# for asin in asins:
#     if asin in in_text_file:
#         continue
#     with open(file_path, "a") as file:
#         file.write(f"{asin}\n")
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from pytz import utc
# from datetime import datetime, timedelta

# async def test_job():
#     print(f"Test job running at {datetime.utcnow()}")
# scheduler = AsyncIOScheduler(timezone=utc)
# scheduler.start()
# while True:
    

#     scheduler.add_job(test_job, 'interval', seconds=30)  # Run every 30 seconds

# # Rest of your asyncio event loop setup...


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio

async def test_job():
    print(f"Test job executed at: {datetime.utcnow()} UTC")

async def main():
    # Create an instance of AsyncIOScheduler
    scheduler = AsyncIOScheduler(timezone="utc")

    # Start the scheduler
    scheduler.start()

    # Add a test job that runs every 10 seconds
    # scheduler.add_job(test_job, 'interval', seconds=10)
    scheduler.add_job(
        test_job, 
        'date', 
        run_date=datetime.utcnow() + timedelta(minutes=2), 
        
    )
    # Keep the script running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass

# Run the main coroutine
if __name__ == "__main__":
    asyncio.run(main())
