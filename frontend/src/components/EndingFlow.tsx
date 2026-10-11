import { useState } from 'react'
import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { HintText } from './HintText'
import { PanelHeader } from './PanelHeader'
import { resolveParagraphs, resolveText } from '../game/textUtils'
import { UI } from '../strings'
import type { Story, GameFields, Rank } from '../game/types'

interface Props {
  endingKey: string
  story: Story
  fields: GameFields
  legendScore: number
  onRestart: () => void
}

function resolveRank(ranks: Rank[], score: number): Rank {
  let best = ranks[0]
  for (const rank of ranks) {
    if (rank.min <= score) best = rank
  }
  return best
}

type Step = 'ending' | 'finale' | 'reveal' | 'score'

export function EndingFlow({ endingKey, story, fields, legendScore, onRestart }: Props) {
  const [step, setStep] = useState<Step>('ending')

  const ending = story.endings[endingKey]
  const endingParagraphs = ending ? resolveParagraphs(ending.paragraphs, fields) : []

  const finaleParagraphs = resolveParagraphs(story.finale.paragraphs, fields)
  const revealParagraphs = resolveParagraphs(story.reveal.paragraphs, fields)

  const rank = resolveRank(story.ranks, legendScore)
  const heritageText = resolveText(story.heritage, fields)
  const lookUpText = resolveText(story.look_up, fields)

  const advance = () => {
    if (step === 'ending') setStep('finale')
    else if (step === 'finale') setStep('reveal')
    else if (step === 'reveal') setStep('score')
  }

  if (step === 'ending') {
    return (
      <>
        <HintText className="mb-4">{UI.ending.hint}</HintText>
        <PixelCard title={ending?.title ?? ''}>
          {endingParagraphs.map((p, i) => (
            <NarrativeText key={i} className="mb-3">{p}</NarrativeText>
          ))}
          <PixelButton tone="gold" className="w-full mt-3" onClick={advance}>
            {UI.ending.continueButton}
          </PixelButton>
        </PixelCard>
      </>
    )
  }

  if (step === 'finale') {
    return (
      <>
        {story.finale.act && <HintText className="mb-4">{story.finale.act}</HintText>}
        <PixelCard title="">
          {finaleParagraphs.map((p, i) => (
            <NarrativeText key={i} className="mb-3">{p}</NarrativeText>
          ))}
          <PixelButton tone="gold" className="w-full mt-3" onClick={advance}>
            {UI.ending.continueButton}
          </PixelButton>
        </PixelCard>
      </>
    )
  }

  if (step === 'reveal') {
    return (
      <>
        <PixelCard title={story.reveal.title}>
          {revealParagraphs.map((p, i) => (
            <NarrativeText key={i} className="mb-3">{p}</NarrativeText>
          ))}
          <PixelButton tone="gold" className="w-full mt-3" onClick={advance}>
            {UI.ending.continueButton}
          </PixelButton>
        </PixelCard>
      </>
    )
  }

  return (
    <>
      <div className="border-2 border-retro-border-strong bg-retro-surface mb-4">
        <PanelHeader label={UI.ending.scoreLabel} />
        <div className="px-6 py-4 flex flex-col gap-2">
          <p className="font-mono text-retro-secondary text-lg font-bold text-center">
            {legendScore} / {UI.scene.totalDecisions}
          </p>
          <p className="font-mono text-retro-secondary text-sm font-semibold text-center">
            {rank.title}
          </p>
          <NarrativeText center className="text-sm">{rank.text}</NarrativeText>
        </div>
      </div>
      {heritageText && (
        <NarrativeText className="mb-3 text-sm">{heritageText}</NarrativeText>
      )}
      {lookUpText && (
        <NarrativeText className="mb-4 text-sm opacity-70">{lookUpText}</NarrativeText>
      )}
      <PixelButton tone="gold" className="w-full" onClick={onRestart}>
        {UI.ending.restartButton}
      </PixelButton>
    </>
  )
}
