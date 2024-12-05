import os
import asyncio
import csv
import details as ds
from telethon.sync import TelegramClient, types
import pandas as pd
from colorama import Fore, Style

api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number

async def scrape_channel_content(channel_name, csv_filename,post_limit, batch_size=1):
    async with TelegramClient(phone, api_id, api_hash) as client:
        try:
            entity = await client.get_entity(channel_name)
            post_count = 0
            batch = []
            count=0
            async for post in client.iter_messages(entity):
                post_count += 1

                text = post.text or ""
                if sender := post.sender:
                    if isinstance(sender, types.User):
                        username = sender.username or "N/A"
                        first_name = sender.first_name or "N/A"
                        last_name = sender.last_name or "N/A"
                        user_id = sender.id
                    else:
                        username = "N/A"
                        first_name = "N/A"
                        last_name = "N/A"
                        user_id = "N/A"
                else:
                    username = "N/A"
                    first_name = "N/A"
                    last_name = "N/A"
                    user_id = "N/A"

                views = post.views or "N/A"
                message_url = f"https://t.me/{channel_name}/{post.id}"

                batch.append((text, username, first_name, last_name, user_id, views, message_url))
                count+=1
                if len(batch) >= batch_size:
                    # Save batch to CSV
                    df = pd.DataFrame(
                        batch,
                        columns=['Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'Message URL']
                    )
                    df.to_csv(csv_filename, mode='a', header=post_count <= batch_size, index=False)
                    batch.clear()

                    print(
                        f"{Fore.WHITE}{post_count} Posts scraped in {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}"
                    )
                
                if(count>=post_limit):
                    return
            if batch:
                df = pd.DataFrame(
                    batch,
                    columns=['Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'Message URL']
                )
                df.to_csv(csv_filename, mode='a', header=False, index=False)
            

            print(f"Finished scraping {Fore.LIGHTYELLOW_EX}{post_count}{Style.RESET_ALL} posts.")

        except Exception as e:
            print(f"An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")


async def extract_user_details(csv_filename, users_csv_filename):
    ids = set()
    
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                ids.add(row['User ID'].strip())
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
        return
    except KeyError:
        print(f"Error: 'User ID' column not found in the file.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    user_details = []

    async with TelegramClient(phone, api_id, api_hash) as client:
        for user_id in ids:
            try:
                if not user_id.isdigit():
                    print(f"Skipping invalid ID: {user_id}")
                    continue
                entity = await client.get_entity(int(user_id))
                if entity.phone is not None:
                    user_details.append({
                        'username': entity.username,
                        'first_name': entity.first_name,
                        'last_name': entity.last_name,
                        'userid': entity.id,
                        'phone': entity.phone
                    })
            except Exception as e:
                print(f"An error occurred for ID {user_id}: {Fore.RED}{e}{Style.RESET_ALL}")

    if user_details:
        with open(users_csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'first_name', 'last_name', 'userid', 'phone'])
            writer.writeheader()
            writer.writerows(user_details)
        
        print(f"All user details saved to {Fore.LIGHTYELLOW_EX}{users_csv_filename}{Style.RESET_ALL}.")


async def main():
    try:
        channel_name = input(
            f"{Fore.CYAN}Please enter a target Telegram channel (e.g., https://t.me/{Fore.LIGHTYELLOW_EX}your_channel{Style.RESET_ALL}):\n"
        )
        print(f'You entered "{Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}"')
        answer = input("Is this correct? (y/n): ")
        if answer.lower() != 'y':
            return
        file_name=input("Enter the file name where you wanted to save data :")
        post_limit=input("Enter the number of posts you want to scrape :")
        output_directory = f"Collection/{file_name}"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        csv_filename = f'{output_directory}/{file_name}_messages.csv'
        users_csv_filename = f'{output_directory}/{file_name}_users.csv'

        print(f'Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')
        hello=await scrape_channel_content(channel_name, csv_filename,post_limit, batch_size=10)

        print(f'Extracting user details from {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}...')
        await extract_user_details(csv_filename, users_csv_filename)

    except Exception as e:
        print(f"An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")


if __name__ == '__main__':
    asyncio.run(main())
