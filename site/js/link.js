// The reset and confirm pages, before they're drawn: does the address carry an email link's token (#t=...)? The page lays itself
// out for one or the other from the start, so nothing jumps once the rest of the page's script runs.
document.documentElement.classList.add(/^#(?:.*&)?t=[^&\s]/.test(location.hash) ? 'has-token' : 'no-token');
