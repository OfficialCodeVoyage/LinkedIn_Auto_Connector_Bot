const puppeteer = require('puppeteer');
const fs = require('fs');

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
    await page.type('#password', "###");
    await page.click('.btn__primary--large');
    await new Promise(r => setTimeout(r, 2000));
    await page.waitForNavigation();
    console.log('Logged in to LinkedIn.');
}

async function performSearch(page) {
    console.log('Navigating to search results page...');
    await page.goto('https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter');
    await page.waitForTimeout(5000);
    console.log('Search results loaded.');
}

async function scrollAndCollectUserLinks(page, maxUsers = 50) {
    let userLinks = new Set();
    let scrollCount = 0;

    while (userLinks.size < maxUsers) {
        const links = await page.$$eval('a[data-control-name="search_srp_result"]', elements =>
            elements.map(el => el.href)
        );

        links.forEach(link => userLinks.add(link));
        console.log(`Links collected so far: ${userLinks.size}`);

        await page.evaluate(`window.scrollBy(0, document.body.scrollHeight)`);
        await page.waitForTimeout(2000);
        scrollCount++;

        if (userLinks.size >= maxUsers) break;
        console.log(`Scroll attempt #${scrollCount} complete.`);
    }

    console.log(`Finished collecting user profile links. Total: ${userLinks.size}`);
    return Array.from(userLinks);
}

async function sendConnectionRequest(page, profileUrl) {
    console.log(`Navigating to user profile: ${profileUrl}`);
    await page.goto(profileUrl);
    await page.waitForTimeout(3000);

    const connectButton = await page.$('button[aria-label*="Connect"]');
    if (connectButton) {
        try {
            console.log(`Found Connect button on profile: ${profileUrl}`);
            await connectButton.click();
            await page.waitForTimeout(2000);

            const addNoteButton = await page.$('span[artdeco-button__text="Add a note"]');

            if (addNoteButton) {
                console.log(`Add a note option found, adding a personalized message.`);
                await addNoteButton.click();
                const message = "Hi, I hope this message finds you well. I'm exploring new opportunities in tech and would love to connect.";
                await page.type('#custom-message', message);
                await page.click('span[artdeco-button__text="Send"]');
            } else {
                console.log(`No Add a note option found, sending request without a note.`);
                await page.click('span[artdeco-button__text="Send"]');
            }

            console.log(`Connection request sent to ${profileUrl}`);
        } catch (error) {
            console.log(`Failed to send connection request to ${profileUrl}: ${error}`);
            fs.appendFileSync('error_log.txt', `Error on ${profileUrl}: ${error}\n`);
        }
    } else {
        console.log(`No Connect button found for ${profileUrl}`);
        fs.appendFileSync('error_log.txt', `No Connect button on ${profileUrl}\n`);
    }
}

async function processUserQueue(page, userQueue) {
    while (userQueue.length > 0) {
        const profileUrl = userQueue.shift();
        await sendConnectionRequest(page, profileUrl);
        await page.waitForTimeout(10000); // Wait between requests to avoid triggering LinkedIn's anti-bot mechanisms
    }
    console.log('All connection requests processed.');
}

(async () => {
    const { browser, page } = await launchBrowser();

    try {
        await loginToLinkedIn(page);
        await performSearch(page);
        const userLinks = await scrollAndCollectUserLinks(page);

        console.log('Starting to process user queue...');
        await processUserQueue(page, userLinks);
    } catch (err) {
        console.log(`Unexpected error: ${err}`);
        fs.appendFileSync('error_log.txt', `Unexpected error: ${err}\n`);
    } finally {
        console.log('Closing browser...');
        await browser.close();
        console.log('Browser closed.');
    }
})();
