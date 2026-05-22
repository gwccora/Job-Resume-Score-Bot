# Job-Resume-Score-Bot
Job hunting made me realize I could simplify checking whether jobs were a good fit for me. Using JobSpy tools, I built basic interfaces that scrape job postings from LinkedIn and Indeed into CSV files. I then use Groq to score job descriptions against my resume. Early mock-up and final versions planned.



Beta

Two different Python codes in a txt file that's your own personal resume to help with the Groq character limit, and a .env file for the security key.

To make this work for you, you will need a .txt file with your resume with its most bare-bones keywords to help with the AI's assessment process later on. Then you need a .env file with this format. This is the only thing needed in this file.

GROQ_API_KEY=your_key_here

Scrapes
<img width="931" height="618" alt="Screenshot 2026-05-22 164006" src="https://github.com/user-attachments/assets/f822f668-0c32-4c24-b60a-520b9541cf26" />




Makes the AI scoring
<img width="1096" height="671" alt="Screenshot 2026-05-22 164151" src="https://github.com/user-attachments/assets/807581c6-6f4f-4271-9f0d-4362f4cce1b2" />
