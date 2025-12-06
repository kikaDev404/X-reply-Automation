import time
import random
from playwright.sync_api import sync_playwright

def human_type(page, text, selector=None):
    """Types text with realistic random delays between keystrokes."""
    if selector:
        page.click(selector)
        time.sleep(random.uniform(0.4, 1.2))

    for char in text:
        page.keyboard.type(char, delay=random.randint(30, 120))
        if random.random() < 0.15:
            time.sleep(random.uniform(0.3, 0.9))


def scrape_current_tweet(page):
    """Scrape username, handle, text, link, likes from the currently focused tweet."""

    return page.evaluate("""() => {
        const tweet = document.activeElement.closest('[role="article"]');
        if (!tweet) return null;

        const getText = (sel) =>
            tweet.querySelector(sel)?.innerText?.trim() || '';
        const getHref = (sel) =>
            tweet.querySelector(sel)?.getAttribute('href') || '';

        // handle from avatar link: /username
        const avatarHref = getHref('[data-testid="Tweet-User-Avatar"] a[role="link"]');
        const handle = avatarHref ? '@' + avatarHref.replace(/^\\//, '') : '';

        // display name from User-Name block
        const username = getText('[data-testid="User-Name"]');

        return {
            username,
            handle,
            text:  getText('div[data-testid="tweetText"]'),
            link:  'https://x.com' + getHref('a[href*="/status/"]:not([href*="photo"])'),
            likes: getText('button[data-testid="like"]'),
        };
    }""")


def like_if_not_liked(page):
    """
    For the currently focused tweet:
      - if already liked: return 'already-liked'
      - if not liked and like button exists: click like and return 'liked'
      - else: return 'no-like-button' / 'no-tweet'
    X uses data-testid='like' for the unliked button and 'unlike' when it is liked.
    """

    randomness = random.uniform(0.5, 1.5)
    time.sleep(0.8 * randomness)

    return page.evaluate("""() => {
        const tweet = document.activeElement.closest('[role="article"]');
        if (!tweet) return { status: 'no-tweet' };

        const unlikeBtn = tweet.querySelector('button[data-testid="unlike"], button[aria-label*="Liked"]');
        if (unlikeBtn) {
            return { status: 'already-liked' };
        }

        const likeBtn = tweet.querySelector('button[data-testid="like"], button[aria-label^="Like"]');
        if (likeBtn) {
            likeBtn.click();
            return { status: 'liked' };
        }

        return { status: 'no-like-button' };
    }""")

def main():
    with sync_playwright() as p:
        print("Connecting to your Chrome (port 9222)...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("Start Chrome with:")
            print("google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/x_test")
            return

        if not browser.contexts:
            print("No contexts found in connected browser.")
            return

        context = browser.contexts[0]
        if not context.pages:
            print("No pages open in first context.")
            return

        page = context.pages[0]

        print("Connected! Make sure you're on an X/Twitter search or timeline page.")
        input("Press Enter when ready to start the test loop...")

        count = 0
        try:
            while True:
                # Move to next *unseen* tweet, skipping ones already liked
                while True:
                    page.keyboard.press("j")
                    time.sleep(1.0)  # allow tweet focus & buttons to update

                    like_state = like_if_not_liked(page)
                    status = like_state.get("status")

                    if status == "already-liked":
                        print("Tweet already liked — skipping to next...")
                        # loop again, press 'j' for next tweet
                        continue
                    elif status == "liked":
                        print("Liked this tweet.")
                        break
                    elif status == "no-like-button":
                        print("No like button found on this item (maybe ad/promo) — skipping...")
                        continue
                    elif status == "no-tweet":
                        print("No tweet container found — skipping...")
                        continue
                    else:
                        print(f"Unexpected like state: {status!r} — skipping...")
                        continue

                count += 1
                print(f"\n--- Test Cycle {count} ---")

                # Scrape the tweet we just liked
                data = scrape_current_tweet(page)
                if data:
                    print(f"@{data['handle']} — {data['username']}")
                    text = data['text'] or ''
                    print(f"{text[:180]}{'...' if len(text) > 180 else ''}")
                    print(f"Link: {data['link']}")
                    print(f"Likes (text): {data['likes']}")
                else:
                    print("No tweet data scraped (structure may have changed).")

                # Optional: open reply, type, then cancel (your original behavior)
                page.keyboard.press("r")
                time.sleep(1.3)
                human_type(page, "gm gm fam")

                print("   Waiting 3 seconds before canceling...")
                time.sleep(3)

                page.keyboard.press("Control+Enter")
                time.sleep(0.8)
                print("   Reply canceled — nothing posted\n")

                stop = input("Press Enter for next tweet (or type 'q' to quit): ")
                if stop.strip().lower() == 'q':
                    break

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"\nError occurred: {e}")

        print(f"\nFinished {count} test cycles. Browser stays open.")
        # Browser stays open so your session is preserved.


if __name__ == "__main__":
    main()
