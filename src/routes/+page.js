export function load({ url }) {
    return {
        metro: url.searchParams.get('metro') || ''
    };
}
