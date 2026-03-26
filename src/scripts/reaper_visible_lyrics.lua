-- reaper_visible_lyrics.lua
-- Convierte lyric events en text events visibles en el item

local item_count = reaper.CountMediaItems(0)

for i = 0, item_count - 1 do

    local item = reaper.GetMediaItem(0, i)
    local take = reaper.GetActiveTake(item)

    if take and reaper.TakeIsMIDI(take) then

        local _, _, _, text_count = reaper.MIDI_CountEvts(take)

        local lyrics = {}

        -- recoger eventos lyric
        for j = 0, text_count - 1 do

            local retval, selected, muted, ppqpos, type, msg =
                reaper.MIDI_GetTextSysexEvt(take, j)

            if type == 5 then
                table.insert(lyrics, {ppq = ppqpos, text = msg})
            end
        end

        -- insertar text events visibles
        for _, lyric in ipairs(lyrics) do

            reaper.MIDI_InsertTextSysexEvt(
                take,
                false,
                false,
                lyric.ppq,
                6,
                lyric.text
            )

        end

        reaper.MIDI_Sort(take)

    end

end

reaper.UpdateArrange()