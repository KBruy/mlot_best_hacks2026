import { useEffect } from 'react'
import { useGame } from '../game/useGame'

export function useGeolocation() {
  const { state, dispatch } = useGame()

  useEffect(() => {
    if (state.demoMode) return
    if (!navigator.geolocation) return

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        dispatch({
          type: 'GPS_UPDATE',
          payload: { lat: pos.coords.latitude, lon: pos.coords.longitude },
        })
      },
      () => {
        // błąd GPS — nie blokujemy gry, po prostu nie ma pozycji
      },
      { enableHighAccuracy: true, maximumAge: 5000 },
    )

    return () => navigator.geolocation.clearWatch(watchId)
  }, [state.demoMode, dispatch])
}
