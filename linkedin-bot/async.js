const puppeteer = require('puppeteer');
const fs = require('fs');
require('dotenv').config();

class LinkedInBot {
    constructor() {
        this.browser = null;
        this.page = null;
        this.requestsSent = 0;
        this.maxRequests = 50;
    }

    async launch() {
        this.browser = await puppeteer.launch({ headless: false });
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });
        this.page.setDefaultTimeout(60000);
    }

    async login(username, password) {
        console.log('Navigating to LinkedIn login page...');
        await this.page.goto('https://www.linkedin.com/login');
        await this.page.type('#username', "#@yahoo.com");
        await this.page.type('#password', "#");
        await this.page.click('.btn__primary--large');
        await new Promise(r => setTimeout(r, 2000));
        await this.page.waitForNavigation();
        console.log('Logged in to LinkedIn.');
    }

    async closeMessagingOverlay() {
        const overlayButton = await this.page.$('button.msg-overlay-bubble-header__control');
        if (overlayButton) {
            console.log('Closing messaging overlay...');
            await overlayButton.click();
        }
    }

    async search(query) {
        console.log(`Navigating to search results page for: ${query}...`);
        await this.page.goto(`https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(query)}`);
        await this.page.waitForTimeout(5000);
    }

    async scrollPage() {
        let previousHeight;
        while (true) {
            previousHeight = await this.page.evaluate('document.body.scrollHeight');
            await this.page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
            await this.page.waitForTimeout(2000);
            let currentHeight = await this.page.evaluate('document.body.scrollHeight');
            if (currentHeight === previousHeight) break;
        }
        console.log('Finished scrolling.');
    }

    async sendRequests() {
        while (this.requestsSent < this.maxRequests) {
            const buttons = await this.page.$$('button span.artdeco-button__text');
            const relevantButtons = buttons.filter(async button =>
                ['Connect', 'Follow', 'Message'].includes(await this.page.evaluate(el => el.textContent.trim(), button))
            );

            console.log(`Found ${relevantButtons.length} relevant buttons.`);
            if (relevantButtons.length === 0) break;

            for (let button of relevantButtons) {
                const buttonText = await this.page.evaluate(el => el.textContent.trim(), button);
                if (buttonText === 'Connect' && this.requestsSent < this.maxRequests) {
                    await this.sendRequest(button);
                }
            }

            const nextPageButton = await this.page.$('button[aria-label="Next"]');
            if (nextPageButton) {
                await nextPageButton.evaluate(b => b.scrollIntoView());
                await nextPageButton.click();
                await this.page.waitForNavigation();
                console.log('Navigated to the next page.');
            } else {
                console.log('No more pages left.');
                break;
            }
        }
    }

    async sendRequest(button) {
        try {
            const parentButton = await button.evaluateHandle(el => el.closest('button'));
            await parentButton.evaluate(b => b.scrollIntoView());
            await parentButton.click();

            try {
                await this.page.waitForSelector('button[aria-label="Add a note"]', { visible: true, timeout: 15000 });
                await this.page.click('button[aria-label="Add a note"]');
                const message = `Hi there,\n\nI hope this message finds you well. I'm exploring new opportunities in tech and would love to connect. I have a strong background in Azure Cloud and Software Development, with a focus on Cloud Engineering and AI/ML.\n\nLooking forward to connecting!\n\nBest regards,\nYour Name`;
                await this.page.type('#custom-message', message);
                await this.page.click('button[aria-label="Send now"]');
            } catch (noteError) {
                console.log('Add a note button not found, sending request without note.');
                await this.page.click('button[aria-label="Send now"]');
            }

            this.requestsSent++;
            console.log(`Requests sent: ${this.requestsSent}`);
            await this.page.waitForTimeout(10000);
        } catch (clickError) {
            console.log(`Error sending connection request: ${clickError}`);
            await this.captureScreenshot('sendRequest-error');
        }
    }

    async captureScreenshot(filename) {
        try {
            await this.page.bringToFront();
            await this.page.screenshot({ path: `${filename}.png` });
            console.log(`Captured screenshot: ${filename}.png`);
        } catch (err) {
            console.log(`Failed to capture screenshot: ${err}`);
        }
    }

    async close() {
        console.log('Closing browser...');
        if (this.browser) await this.browser.close();
        console.log('Browser closed.');
    }

    async run() {
        try {
            await this.launch();
            await this.login(process.env.LINKEDIN_USERNAME, process.env.LINKEDIN_PASSWORD);
            await this.closeMessagingOverlay();
            await this.search('tech recruiter');
            await this.scrollPage();
            await this.sendRequests();
        } catch (err) {
            console.log(`Unexpected error: ${err}`);
            await this.captureScreenshot('unexpected-error');
        } finally {
            await this.close();
        }
    }
}

(async () => {
    const bot = new LinkedInBot();
    await bot.run();
})();
