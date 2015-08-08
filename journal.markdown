## Initial Tweaks ##
Tue 04 Aug 2015 06:55:29 PM EDT

First thing: change the "NEW GAME" text in the main menu. I chose that because
it was easy to find (`git grep "NEW GAME"`) and because it appears right after
the title screen. That second point got me thinking about something that's
going to be essential to further study: figuring out how to "CONTINUE" into
arbitrary places with arbitrary items, pokémon, etc. It's bad enough having to
look at the GAME FREAK logo every time, but having to sit through Oak's intro
would be ridiculous.

I first tried tweaking the "NEW GAME" text without changing its length. It
worked. Then I tried extending it. That worked too. Then I tried *really*
extending it. That also worked, and wrapped text automatically. However, it did
break out of the menu's border.

The next thing I couldn't resist messing with was the music. The title theme is
in `audio/music/titlescreen.asm`. Yes, the music is encoded in `.asm` files as
well. But the language looks like MIDI or something like it. I wonder if the
Game Boy understands this, or if each cartridge has to write its own MIDI
interpretation code. I'm guessing the latter? Anyway, I first tried changing
around the numbers next to the notes (`G_`, `B_`, etc.). The numbers represent
duration. I haven't tested it yet, but I believe the following must be the
opening notes of the lead melody:

    Music_TitleScreen_branch_7e622::
        notetype 12, 14, 7
        octave 3
        G_ 6
        B_ 2
        octave 4
        D_ 8
        notetype 12, 9, 5
        endchannel

    Music_TitleScreen_branch_7e62c::
        notetype 12, 14, 7
        octave 4
        F_ 6
        E_ 1
        D# 1
        D_ 8
        notetype 12, 9, 5
        endchannel

The last thing I messed with was the pokémon that slide onto the title screen.
I found them defined in `data/title_mons.asm`. I thought it might be fun to
change them all to `JYNX`, but that didn't quite work -- it showed a Charmander
initially (as it always seems to), then a Jynx, and then a blank. Next I tried
deleting them all and adding only `JYNX` and `MR_MIME`. It showed a Jynx once,
but it also showed other pokémon. I'm wondering if the length of the list to
draw from is hardcoded somewhere, so it "overflowed" into the lists for the
Green and/or Blue versions.

...

OK, so it always starts with Charmander because it is hardcoded. Changing 
everything to `JYNX` didn't work because the code that chooses the next pokémon 
makes sure it doesn't repeat itself. Note the comment:

    .loop
    ; Keep looping until a mon different from the current one is picked.
        call Random
        and $f
        ld c, a
        ld b, 0
        ld hl, TitleMons
        add hl, bc
        ld a, [hl]
        ld hl, wTitleMonSpecies

    ; Can't be the same as before.
        cp [hl]
        jr z, .loop

Here's how I think the random selection works:

  * `Random` produces a random 16-bit number
  * `and $f` keeps only the right-most nibble, bounding the value at 15
  * this result, which will act as an offset, is placed in `bc`
  * the address of TitleMons is placed in `hl`
  * the numbers are added to get the address of the random pokémon
  * the pokémon identifier at that address is placed in `a`
  * the previous pokémon identifier is placed in `hl`
  * basically we ask `hl == a` by subtracting `hl` from `a` and checking to see
    if it's zero
  * if so, we try again

So when we initially removed all the entries from `TitleMons` and added two of
our own, we were indeed seeing an "overflow" of sorts. At least I think you'd 
call it an overflow. Or an "out-of-bounds". To fix this, we have to change the 
argument to `and`. If I want to choose between two pokémon, I'd do `and $1`, 
because we only want a single random bit. The Jynx/Mime patch is at 
`patches/jynx_mime_title_screen.patch`.


## Save File Manipulation ##
Wed 05 Aug 2015 11:19:58 PM EDT

I think the key to jumping into whichever situation I want with whichever 
pokémon I want will be manipulating the save file. That's one way to do it, 
anyway. VisualBoyAdvance makes a save file in `~/.vba` and names it after the 
ROM you're using. I haven't quite figured out which parts of the Game Boy's 
memory are saved in here, but I was able to find the player name after saving a 
file. I tried changing the name without changing its length (`ASH` to `JIM`), 
but that didn't work, presumably because there's a checksum in there that I 
didn't recalculate. That will be the next thing I try.


## Changing Player Name ##
Sat 08 Aug 2015 07:09:49 PM EDT

I was able to change the player name in the save file! This consisted of first 
changing the name, then updating the checksum accordingly. I didn't change the 
length of the name -- though maybe I'll try that next. I just went from `ASH` 
to `ASS`. I tried to manually step through the `SAVCheckSum` function, but I 
saw that it was going to involve many iterations. So I wrote a little python 
script to do it for me. I initialized the registers exactly as they would be in 
the game, and walked through the actual `pokered.sav` file. I first tested to 
see if it would give me the same result as what was already in the file, and it 
did! Then I changed the name and reran it, updated the checksum accordingly, 
and it worked! I could easily take it a step further and have it automatically 
write the new checksum to the file. I feel like this is a nice first step in 
modifying the save file however I want, though a small one for sure.

One other note -- I could have opted instead to modify the game code to use the 
`LoadSAVIgnoreBadCheckSum` routine that already exists, but I ran into 
difficulty. The current `LoadSAV` function that I'd have to swap out is special 
for some reason. It's not called with `call`, but instead some macro called 
`predef`. I followed the code for the "predef" process and I'm still not really 
clear on what it's doing. It's "predefining" somehow, but I don't know what 
that means. I tried just `call`ing `LoadSAVIgnoreBadCheckSum`, but that blew 
up. I'll probably have to revisit `predef` at some point.
