car-search
==========

I used this to search for Toyota Camry and Toyota Corolla cars. If you want to use other cars and have it return the edmund's TMV, you have to bring in the style numbers edmunds uses on its site. This was more hacky than I would have liked, but I would bring up the page I wanted the style for (e.g. http://www.edmunds.com/toyota/camry/2012/tmv-appraise.html) and then run the function in tmv.js after the page loaded. Then I put all the style ids for car, year, and body type in cars.py . The style ids all come down in the html file, but it's in javascript that gets executed. Since I was just looking for a few cars I didn't parse it in my script but got all of the values I was interested in beforehand and put them in the script.

I added the script to a cron job that ran every three minutes. If there are any new cars that met my criteria, it would send an email with the old and new cars, it's price, year, color, mileage, etc, and true-market-value.

If you want it to send an email, uncomment the last few lines and add your email address in. Caution: many ISPs block sending emails from localhost, so you may have to set it up to send from a non-localhost email. Also, for emails I created a filter in my email account to never send an email with this exact subject to my spam folder. Make sure to do that or your email provider will probably mark it as spam pretty quickly and you won't see the updates.

Enjoy!

https://lucid.app/documents/view/f25fe4c9-faa0-4538-8c60-e2f7ec9ed5c6
