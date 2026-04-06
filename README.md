# Learn to Write

A simple browser game that fetches images as you type words — helping you learn to spell through visual association.

## Running

No installation or server required. Just open the file in a browser:

```
open index.html
```

Or double-click `index.html` in your file manager.

## How to play

1. A word appears on screen with greyed-out letters.
2. Type the word — each correct letter lights up green; wrong letters turn red.
3. After 2+ correct letters, a matching image is fetched and displayed.
4. Complete the word to move on. Press **Next** to skip.
5. Add your own words using the input at the bottom.

## Notes

- Images are fetched from [LoremFlickr](https://loremflickr.com) — no API key needed.
- An internet connection is required to load images.
- All progress is session-only (refreshing the page resets the game).
