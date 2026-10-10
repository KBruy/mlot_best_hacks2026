import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'

function App() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <PixelCard title="Żywy Bestiariusz Wrocławia" className="w-full max-w-xl">
        <p className="narrative mb-8 text-center">
          Dawno temu, gdy Wrocław krył w swych murach więcej tajemnic niż kamieni...
        </p>
        <PixelStack gap="sm">
          <PixelButton tone="gold" className="w-full" onClick={() => {}}>
            Podążaj za Krasnoludem w głąb piwnicy
          </PixelButton>
          <PixelButton tone="gold" className="w-full" onClick={() => {}}>
            Wejdź do Piwnicy Świdnickiej i czekaj na znak
          </PixelButton>
          <PixelButton tone="neutral" className="w-full" disabled>
            Opcja zablokowana
          </PixelButton>
          <PixelButton tone="gold" className="w-full" onClick={() => {}}>
            Wróć do karczmy przy Rynku i zapytaj starego kronikarza o znaczenie znaku na murze
          </PixelButton>
        </PixelStack>
      </PixelCard>
    </main>
  )
}

export default App
