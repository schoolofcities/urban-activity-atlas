for f in Weekend_Difference/*.png; do convert "$f" -resize 700x "Weekend_Difference_small/$(basename "$f")"; done
for f in Weekday_Difference/*.png; do convert "$f" -resize 700x "Weekday_Difference_small/$(basename "$f")"; done
