const puppeteer = require('puppeteer');

async function launchBrowser() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    page.setDefaultTimeout(60000);

    // Clear the browser cache
    await clearBrowserCache(page);

    return { browser, page };
}

async function clearBrowserCache(page) {
    const client = await page.target().createCDPSession();
    await client.send('Network.clearBrowserCache');
    console.log('Browser cache cleared.');
}

async function loginToLinkedIn(page) {
    console.log('Navigating to LinkedIn login page...')
    await page.goto('https://www.linkedin.com/login');
    await page.type('#username', "№@yahoo.com");
    await page.type('#password', "№");
    await page.click('.btn__primary--large');
    await page.waitForTimeout(5000); // Wait for login to complete
    await page.waitForNavigation();
    console.log('Logged in to LinkedIn.');
}

async function performSearch(page) {
    console.log('Navigating to search results page...');
    await page.goto('https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter');
    await page.waitForTimeout(5000); // Wait for search results to load
}

async function sendConnectionRequests(page, maxRequests = 10) {
    const xpaths = [
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[1]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[2]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[3]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[4]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[5]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[6]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div/2/div/div[1]/main/div/div/div[2]/div/ul/li[7]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[8]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[9]/div/div/div/div[3]/div/button",
        "/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[10]/div/div/div/div[3]/div/button"
    ];

    let requestsSent = 0;

    for (let xpath of xpaths) {
        if (requestsSent >= maxRequests) break;

        try {
            const [button] = await page.$x(xpath);
            if (!button) {
                console.log(`Button not found for XPath: ${xpath}`);
                continue;
            }

            const buttonText = await page.evaluate(el => el.textContent.trim(), button);
            if (buttonText === 'Connect') {
                console.log(`Clicking "Connect" button for XPath: ${xpath}`);
                await button.evaluate(b => b.scrollIntoView());
                await button.click();
                await page.waitForTimeout(2000); // Wait for any popups

                // Attempt to add a note, if possible
                try {
                    await page.waitForSelector('span[artdeco-button__text="Add a note"]', { visible: true, timeout: 15000 });
                    await page.click('span[artdeco-button__text="Add a note"]');
                    const message = `Hi,\n\nI hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.\n\nLooking forward to connecting!\n\nBest regards,\nYour Name`;
                    await page.type('#custom-message', message);
                    await page.click('span[artdeco-button__text="Send"]');
                } catch (noteError) {
                    console.log('Add a note button not found, sending request without note.');
                    await page.click('span[artdeco-button__text="Send"]');
                }

                requestsSent++;
                console.log(`Requests sent: ${requestsSent}`);
                await page.waitForTimeout(10000);
            } else {
                console.log(`Skipping non-"Connect" button for XPath: ${xpath}`);
            }
        } catch (error) {
            console.log(`Error handling button for XPath: ${xpath}, Error: ${error}`);
        }
    }
}

(async () => {
    const { browser, page } = await launchBrowser();

    try {
        await loginToLinkedIn(page);
        await performSearch(page);
        await sendConnectionRequests(page);
    } catch (err) {
        console.log(`Unexpected error: ${err}`);
    } finally {
        console.log('Closing browser...');
        await browser.close();
        console.log('Browser closed.');
    }
})();
