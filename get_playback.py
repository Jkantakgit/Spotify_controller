from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import winrt.windows.media.control as wmc
import asyncio


async def get_media_info():
    sessions = await MediaManager.request_async()

    current_session = sessions.get_current_session()
    if current_session:  # there needs to be a media session running
        if wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus["PAUSED"] == current_session.get_playback_info().playback_status:
            return False
        else:
            return True


print(asyncio.run(get_media_info()))
