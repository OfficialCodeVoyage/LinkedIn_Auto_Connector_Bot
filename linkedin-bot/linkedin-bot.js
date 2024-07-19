const puppeteer = require('puppeteer');
const fs = require('fs');

const LINKEDIN_USERNAME = '@@yahoo.com';
const LINKEDIN_PASSWORD = '@';
const SEARCH_LINK = 'https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter';
const BASE_CONNECTION_MESSAGE = `Hi {name},

I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.

Looking forward to connecting!

Best regards,
Your Name
`;

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    page.setDefaultTimeout(10000); // Increase default timeout to 60 seconds

    // Log in to LinkedIn
    await page.goto('https://www.linkedin.com/login');
    await page.type('#username', LINKEDIN_USERNAME);
    await page.type('#password', LINKEDIN_PASSWORD);
    await page.click('.btn__primary--large');
    await page.waitForNavigation();

    // Go to search results page
    await page.goto(SEARCH_LINK);

    let requestsSent = 0;
    const maxRequests = 50;

    while (requestsSent < maxRequests) {
        try {
            // Wait for search results to load
            await page.waitForSelector('.reusable-search__entity-result-list', { timeout: 60000 });
            console.log('Search results loaded.');

            // Get all "Connect" buttons
            const connectButtons = await page.$x("//span[text()='Connect' and contains(@class, 'artdeco-button__text')]/ancestor::button");

            console.log(`Found ${connectButtons.length} Connect buttons on the page.`);
            connectButtons.forEach((button, index) => {
                console.log(`Button ${index + 1}: ${button}`);
            });

            if (connectButtons.length === 0) {
                console.log('No Connect buttons found on this page.');
                // Check if there is a next page
                const nextPageButton = await page.$('button[aria-label="Next"]');
                if (nextPageButton) {
                    await nextPageButton.click();
                    await page.waitForNavigation();
                    continue;
                } else {
                    console.log('No more pages left.');
                    break;
                }
            }

            for (let button of connectButtons) {
                if (requestsSent >= maxRequests) break;

                try {
                    // Scroll into view and click the Connect button
                    await button.evaluate(b => b.scrollIntoView());
                    await button.click();

                    // Wait for the "Add a note" button to appear and click it
                    await page.waitForSelector('button[aria-label="Add a note"]', { timeout: 10000 });
                    await page.click('button[aria-label="Add a note"]');

                    // Get recruiter's name
                    const recruiterName = await page.evaluate(button => {
                        const parentDiv = button.closest('.entity-result__item');
                        const nameElement = parentDiv.querySelector('.entity-result__title-text a span[1]');
                        return nameElement ? nameElement.innerText.trim() : 'there';
                    }, button);

                    // Type and send the connection message
                    const message = BASE_CONNECTION_MESSAGE.replace('{name}', recruiterName);
                    await page.type('#custom-message', message);
                    await page.click('button[aria-label="Send now"]');

                    console.log(`Connection request sent to ${recruiterName}.`);
                    requestsSent++;
                    await page.waitForTimeout(10000); // Wait 10 seconds between requests
                } catch (e) {
                    console.log(`Error sending connection request: ${e}`);
                    continue;
                }
            }

            // Go to the next page
            const nextPageButton = await page.$('button[aria-label="Next"]');
            if (nextPageButton) {
                await nextPageButton.click();
                await page.waitForNavigation();
            } else {
                console.log('No more pages left.');
                break;
            }
        } catch (e) {
            console.log(`Error during operation: ${e}`);
            const pageContent = await page.content();
            fs.writeFileSync('pageContent.html', pageContent); // Save the current page content to analyze the issue
            break;
        }
    }

    await browser.close();
})();
