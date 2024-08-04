const puppeteer = require('puppeteer');

const LINKEDIN_USERNAME = '#@yahoo.com';
const LINKEDIN_PASSWORD = '#';
const SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22103644278%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&searchId=3226caea-b928-4aec-9985-46e505d5f6b7&sid=3C5';

const BASE_CONNECTION_MESSAGE = `Hi there,

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Pavlo Bondarenko
`;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    page.waitForTimeout = async function (number) {
        
    };
    try {
        // Login to LinkedIn
        await page.goto('https://www.linkedin.com/login');
        await page.type('#username', LINKEDIN_USERNAME);
        await page.type('#password', LINKEDIN_PASSWORD);
        await page.click('.btn__primary--large');

        // Wait for 10 seconds to manually enter CAPTCHA if needed
        await page.waitForTimeout(10000);

        await page.waitForNavigation();

        // Navigate to the search link
        await page.goto(SEARCH_LINK, { waitUntil: 'networkidle2' });

        // Wait for the search results to load
        await page.waitForSelector('.search-results__list', { timeout: 60000 });

        let requestsSent = 0;
        const maxRequests = 50;

        while (requestsSent < maxRequests) {
            const buttons = await page.$$('.entity-result__actions button');

            for (const button of buttons) {
                if (requestsSent >= maxRequests) break;

                // Scroll to the button
                await page.evaluate(element => {
                    element.scrollIntoView();
                }, button);

                // Check the text content of the button
                const buttonText = await page.evaluate(el => el.innerText, button);

                if (buttonText.toLowerCase() === 'connect') {
                    await button.click();
                    await page.waitForSelector('button[aria-label="Add a note"]');
                    await page.click('button[aria-label="Add a note"]');
                    await page.type('#custom-message', BASE_CONNECTION_MESSAGE);
                    await page.click('button[aria-label="Send now"]');
                    requestsSent += 1;
                    await page.waitForTimeout(5000); // Sleep for 5 seconds after sending each connection request
                } else if (buttonText.toLowerCase() === 'follow') {
                    await button.click();
                    await page.waitForTimeout(5000); // Sleep for 5 seconds after following each user
                }
            }

            // Scroll to the bottom of the page
            await page.evaluate(() => {
                window.scrollTo(0, document.body.scrollHeight);
            });

            // Navigate to the next page
            const nextPageButton = await page.$('button[aria-label="Next"]');
            if (nextPageButton) {
                await nextPageButton.click();
                await page.waitForNavigation({ waitUntil: 'networkidle2' });
            } else {
                break;
            }
        }

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        await browser.close();
    }
})();
