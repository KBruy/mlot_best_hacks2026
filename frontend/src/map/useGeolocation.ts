import { useEffect } from 'react'
import { useGame } from '../game/useGame'

export function useGeolocation() {
  const { dispatch } = useGame()

  useEffect(() => {
    if (!navigator.geolocation) {
      dispatch({ type: 'GPS_DENIED' })
      return
    }

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        dispatch({
          type: 'GPS_UPDATE',
          payload: { lat: pos.coords.latitude, lon: pos.coords.longitude },
        })
      },
      (err) => {
        // Only permanently deny when the user explicitly refused — timeouts and
        // "position unavailable" are transient; watchPosition will keep retrying.
        if (err.code === GeolocationPositionError.PERMISSION_DENIED) {
          dispatch({ type: 'GPS_DENIED' })
        }
      },
      { enableHighAccuracy: true, maximumAge: 5000 },
    )

    return () => navigator.geolocation.clearWatch(watchId)
  }, [dispatch])
}
