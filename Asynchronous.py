import asyncio
import aiohttp
import time
import csv
import logging
from bs4 import BeautifulSoup
from tabulate import tabulate

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# รายชื่อเว็บไซต์ที่ต้องการดึงข้อมูล
websites = [
    "https://www.dev.to",
    "https://www.reddit.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://www.github.com",

]

# ฟังก์ชันดึงข้อมูลจากแต่ละ URL
async def fetch(url, session):
    try:
        start_time = time.time()  # เริ่มการจับเวลา
        async with session.get(url) as response:
            title = "No title found"
            if response.status == 200:
                html = await response.text()
                title = html.split('<title>')[1].split('</title>')[0]
            elapsed_time = time.time() - start_time 
            return {
                'url': url,
                'title': title,
                'status': response.status,
                'time': elapsed_time
            }
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return {
            'url': url,
            'title': 'N/A',
            'status': 500,
            'time': 0
        }

# ฟังก์ชันหลักในการดึงข้อมูลจากทุกเว็บไซต์
async def fetch_all():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(url, session) for url in websites]
        results = await asyncio.gather(*tasks)
        return results

# ฟังก์ชันในการบันทึกข้อมูลลงใน CSV
def save_to_csv(results):
    with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'status', 'time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                'url': result['url'],
                'title': result['title'],
                'status': result['status'],
                'time': f"{result['time']:.2f}s"
            })

# ฟังก์ชันในการแสดงผลสรุป
def display_summary(results, total_time):
    print("\nResults:")
    print("+----------------------------+-------------------------------------------------------------------------------+----------+--------+")
    print("| URL                        | Title                                                                         |   Status | Time   |")
    print("+============================+===============================================================================+==========+========+")
    for result in results:
        print(f"| {result['url']:<26} | {result['title']:<79} | {result['status']:<8} | {result['time']:.2f} |")
    print("+----------------------------+-------------------------------------------------------------------------------+----------+--------+")
    
    # สรุปการทำงาน
    print("\nSummary:")
    print(f"Total websites processed: {len(results)}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Average time per website: {total_time/len(results):.2f} seconds")

    # คำนวณเวลาที่ประหยัดได้เมื่อเทียบกับการทำงานแบบ synchronous
    total_individual_time = sum(result['time'] for result in results)
    time_saved = total_individual_time - total_time
    print(f"Time saved compared to synchronous execution: {time_saved:.2f} seconds")

# ฟังก์ชันหลักที่ทำงาน
async def main():
    results = await fetch_all()

    total_time = sum(result['time'] for result in results)# เวลาที่ใช้ในการทำงานทั้งหมด
    save_to_csv(results)  # บันทึกผลลัพธ์ลงในไฟล์ CSV
    display_summary(results, total_time)  # แสดงผลสรุป

    logging.info(f"Results saved to http_headers.csv")
    logging.info(f"Total execution time: {total_time:.2f} seconds")

# เรียกใช้งานโปรแกรม
if __name__ == "__main__":
    asyncio.run(main())