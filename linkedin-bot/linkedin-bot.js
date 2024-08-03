const puppeteer = require('puppeteer');
const fs = require('fs');
require('dotenv').config();

async function launchBrowser() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    page.setDefaultTimeout(60000);
    return { browser, page };
}

async function loginToLinkedIn(page) {
    console.log('Navigating to LinkedIn login page...');
    await page.goto('https://www.linkedin.com/login');
    await page.type('#username', "#@yahoo.com");
    await page.type('#password', "#");
    await page.click('.btn__primary--large');
    await new Promise(r => setTimeout(r, 2000));
    await page.waitForNavigation();
    console.log('Logged in to LinkedIn.');
}

async function handleOverlays(page) {
    const messagingOverlayCloseButton = await page.$('button.msg-overlay-bubble-header__control');
    if (messagingOverlayCloseButton) {
        console.log('Messaging overlay found. Closing it...');
        await messagingOverlayCloseButton.click();
    }
}

async function performSearch(page) {
    console.log('Navigating to search results page...');
    await page.goto('https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter');
    await page.waitForTimeout(5000);
}

async function scrollPage(page) {
    let previousHeight;
    while (true) {
        previousHeight = await page.evaluate('document.body.scrollHeight');
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
        await page.waitForTimeout(2000);
        let currentHeight = await page.evaluate('document.body.scrollHeight');
        if (currentHeight === previousHeight) break;
    }
    console.log('Finished scrolling.');
}

async function sendConnectionRequests(page, maxRequests = 50) {
    let requestsSent = 0;

    while (requestsSent < maxRequests) {
        const buttons = await page.$$('button span.artdeco-button__text');
        const relevantButtons = [];

        for (let i = 0; i < buttons.length; i++) {
            const buttonText = await page.evaluate(el => el.textContent.trim(), buttons[i]);
            if (['Connect', 'Follow', 'Message'].includes(buttonText)) {
                relevantButtons.push(buttons[i]);
            }
        }

        console.log(`Filtered to ${relevantButtons.length} relevant buttons.`);
        if (relevantButtons.length === 0) break;

        for (let button of relevantButtons) {
            const buttonText = await page.evaluate(el => el.textContent.trim(), button);
            if (buttonText === 'Connect' && requestsSent < maxRequests) {
                try {
                    const parentButton = await button.evaluateHandle(el => el.closest('button'));
                    await parentButton.evaluate(b => b.scrollIntoView());
                    await parentButton.click();

                    try {
                        await page.waitForSelector('button[aria-label="Add a note"]', { visible: true, timeout: 15000 });
                        await page.click('button[aria-label="Add a note"]');
                        const message = `Hi there,\n\nI hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.\n\nLooking forward to connecting!\n\nBest regards,\nYour Name`;
                        await page.type('#custom-message', message);
                        await page.click('button[aria-label="Send now"]');
                    } catch (noteError) {
                        console.log('Add a note button not found, sending request without note.');
                        await page.click('button[aria-label="Send now"]');
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
            await nextPageButton.evaluate(b => b.scrollIntoView());
            await nextPageButton.click();
            await page.waitForNavigation();
            console.log('Navigated to the next page.');
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
        await handleOverlays(page);
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
