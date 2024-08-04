const puppeteer = require('puppeteer');

describe('LinkedIn Automation Tests', () => {
    let browser;
    let page;

    beforeAll(async () => {
        browser = await puppeteer.launch({ headless: false });
        page = await browser.newPage();
        page.setViewport({ width: 1920, height: 1080 });
        page.setDefaultTimeout(60000); // 60 seconds timeout
    });

    afterAll(async () => {
        await browser.close();
    });

    test('Successful Login Test', async () => {
        console.log('Navigating to LinkedIn login page...');
        await page.goto('https://www.linkedin.com/login');
        await page.type('#username', '#@yahoo.com');
        await page.type('#password', '#');
        await page.click('.btn__primary--large');

        await page.waitForNavigation();
        expect(page.url()).toBe('https://www.linkedin.com/feed/');
    });

    test('CAPTCHA Handling Test', async () => {
        // Navigate to the login page first
        await page.goto('https://www.linkedin.com/login');
        await page.type('#username', '#@yahoo.com');
        await page.type('#password', '#');
        await page.click('.btn__primary--large');
        // Wait for a CAPTCHA or navigation
        const navigationPromise = page.waitForNavigation();
        const captchaDetected = await page.$('div#captcha-internal') !== null;
        if (captchaDetected) {
            console.log('CAPTCHA detected. Waiting for manual solving...');
            await navigationPromise; // Wait for user to solve CAPTCHA manually
        }
        expect(captchaDetected).toBe(false);
    });

    test('Dynamic Content Loading Test', async () => {
        await page.goto('https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&sid=%40g!');
        let previousHeight;
        let currentHeight;
        do {
            previousHeight = await page.evaluate('document.body.scrollHeight');
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
            await page.waitForTimeout(2000); // Wait for 2 seconds to load new content
            currentHeight = await page.evaluate('document.body.scrollHeight');
        } while (currentHeight !== previousHeight);
        expect(currentHeight).toBeGreaterThan(0);
    });

    test('Connection Request Sending Test', async () => {
        // Find the first "Connect" button and click it
        const connectButton = await page.$x("//button[contains(., 'Connect')]");
        if (connectButton.length > 0) {
            await connectButton[0].click();
            await page.waitForSelector('button[aria-label="Send now"]', { visible: true });
            await page.click('button[aria-label="Send now"]');
            console.log('Connection request sent.');
        } else {
            console.log('No Connect button found.');
        }
        expect(connectButton.length).toBeGreaterThan(0);
    });

    test('Next Page Navigation Test', async () => {
        const nextPageButton = await page.$('button[aria-label="Next"]');
        if (nextPageButton) {
            await nextPageButton.click();
            await page.waitForNavigation();
            expect(page.url()).toMatch(/search\/results\/people/);
        } else {
            console.log('No Next button found.');
            expect(nextPageButton).toBe(null);
        }
    });

    test('Invalid Credentials Test', async () => {
        await page.goto('https://www.linkedin.com/login');
        await page.type('#username', 'invalid-email@example.com');
        await page.type('#password', 'wrong-password');
        await page.click('.btn__primary--large');
        await page.waitForSelector('#error-for-username', { visible: true });
        const errorMessage = await page.$eval('#error-for-username', el => el.textContent.trim());
        expect(errorMessage).toMatch(/we couldn't find a LinkedIn account associated with this email/i);
    });
});
