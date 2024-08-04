const puppeteer = require('puppeteer');

async function launchBrowser() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    page.setDefaultTimeout(60000);
    return { browser, page };
}

async function loginToLinkedIn(page) {
    console.log('Navigating to LinkedIn login page...');
    await page.goto('https://www.linkedin.com/login');
    await page.type('#username', "#@yahoo.com");
    await page.type('#password', "#");
    await page.click('.btn__primary--large');
    await new Promise(r => setTimeout(r, 5000));
    await page.waitForNavigation();
    console.log('Logged in to LinkedIn.');
}

async function performSearch(page) {
    console.log('Navigating to search results page...');
    await page.goto('https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter');
    await page.waitForTimeout(5000);
}

async function scrollPage(page) {
    let previousHeight = 0;
    let increment = 100; // Adjust this value to control the scroll speed
    while (true) {
        await page.evaluate(`window.scrollBy(0, ${increment})`);
        await page.waitForTimeout(500); // Adjust this value for speed control

        let currentHeight = await page.evaluate('window.scrollY + window.innerHeight');
        let totalHeight = await page.evaluate('document.body.scrollHeight');

        if (currentHeight >= totalHeight) break;

        previousHeight = currentHeight;
    }
    console.log('Finished scrolling slowly.');
}

async function sendConnectionRequests(page, maxRequests = 50) {
    let requestsSent = 0;

    while (requestsSent < maxRequests) {
        const buttons = await page.$$('button[aria-label^="Invite"]');

        if (buttons.length === 0) {
            console.log('No "Connect" buttons found on this page.');
            break;
        }

        for (let button of buttons) {
            const ariaLabel = await page.evaluate(el => el.getAttribute('aria-label'), button);
            const userName = ariaLabel.split(' ')[1]; // Extracting the user's name

            if (ariaLabel.includes('Connect') && requestsSent < maxRequests) {
                try {
                    console.log(`Attempting to connect with ${userName}...`);
                    await button.evaluate(b => b.scrollIntoView());
                    await button.click();
                    await page.waitForTimeout(2000); // Wait for any popups

                    // Attempt to add a note, if possible
                    try {
                        await page.waitForSelector('span[artdeco-button__text="Add a note"]', { visible: true, timeout: 15000 });
                        await page.click('span[artdeco-button__text="Add a note"]');
                        const message = `Hi ${userName},\n\nI hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.\n\nLooking forward to connecting!\n\nBest regards,\nYour Name`;
                        await page.type('#custom-message', message);
                        await page.click('span[artdeco-button__text="Send"]');
                    } catch (noteError) {
                        console.log('Add a note button not found, sending request without note.');
                        await page.click('span[artdeco-button__text="Send"]');
                    }

                    requestsSent++;
                    console.log(`Requests sent: ${requestsSent}`);
                    await page.waitForTimeout(10000);
                } catch (clickError) {
                    console.log(`Error sending connection request: ${clickError}`);
                    continue;
                }
            }
        }

        const nextPageButton = await page.$('button[aria-label="Next"]');
        if (nextPageButton) {
            console.log('Navigating to the next page...');
            await nextPageButton.evaluate(b => b.scrollIntoView());
            await nextPageButton.click();
            await page.waitForNavigation();
        } else {
            console.log('No more pages left.');
            break;
        }
    }
}

(async () => {
    const { browser, page } = await launchBrowser();

    try {
        await loginToLinkedIn(page);
        await performSearch(page);
        await scrollPage(page);
        await sendConnectionRequests(page);
    } catch (err) {
        console.log(`Unexpected error: ${err}`);
    } finally {
        console.log('Closing browser...');
        await browser.close();
        console.log('Browser closed.');
    }
})();
