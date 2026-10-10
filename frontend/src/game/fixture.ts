import type { Story } from './types'

// Mock — zastąpić danymi z backendu gdy kontrakt zostanie ustalony (task F3-2)
export const fixture: Story = {
  id: 'legenda-placeholder',
  title: 'Legenda Wrocławska',
  intro: 'Dawno temu we Wrocławiu...',
  characters: [
    {
      id: 'postac-a',
      name: 'Postać A',
      description: 'Opis postaci A.',
      entry_node_id: 'scena-1a',
    },
    {
      id: 'postac-b',
      name: 'Postać B',
      description: 'Opis postaci B.',
      entry_node_id: 'scena-1b',
    },
  ],
  nodes: [
    {
      id: 'scena-1a',
      type: 'decision',
      text: 'Scena 1 — perspektywa postaci A. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c1a-1', text: 'Opcja 1 dla postaci A', consequence: 'Konsekwencja opcji 1A.', next_node_id: 'scena-2' },
        { id: 'c1a-2', text: 'Opcja 2 dla postaci A', consequence: 'Konsekwencja opcji 2A.', next_node_id: 'scena-2' },
      ],
    },
    {
      id: 'scena-1b',
      type: 'decision',
      text: 'Scena 1 — perspektywa postaci B. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c1b-1', text: 'Opcja 1 dla postaci B', consequence: 'Konsekwencja opcji 1B.', next_node_id: 'scena-2' },
        { id: 'c1b-2', text: 'Opcja 2 dla postaci B', consequence: 'Konsekwencja opcji 2B.', next_node_id: 'scena-2' },
      ],
    },
    {
      id: 'scena-2',
      type: 'decision',
      text: 'Scena 2 — wspólna. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c2-1', text: 'Opcja 1', consequence: 'Konsekwencja 1.', next_node_id: 'scena-3' },
        { id: 'c2-2', text: 'Opcja 2', consequence: 'Konsekwencja 2.', next_node_id: 'scena-3' },
      ],
    },
    {
      id: 'scena-3',
      type: 'decision',
      text: 'Scena 3 — wspólna. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c3-1', text: 'Opcja 1', consequence: 'Konsekwencja 1.', next_node_id: 'scena-4' },
        { id: 'c3-2', text: 'Opcja 2', consequence: 'Konsekwencja 2.', next_node_id: 'scena-4' },
      ],
    },
    {
      id: 'scena-4',
      type: 'decision',
      text: 'Scena 4 — wspólna. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c4-1', text: 'Opcja 1', consequence: 'Konsekwencja 1.', next_node_id: 'scena-5' },
        { id: 'c4-2', text: 'Opcja 2', consequence: 'Konsekwencja 2.', next_node_id: 'scena-5' },
      ],
    },
    {
      id: 'scena-5',
      type: 'decision',
      text: 'Scena 5 — wspólna. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c5-1', text: 'Opcja 1', consequence: 'Konsekwencja 1.', next_node_id: 'scena-6' },
        { id: 'c5-2', text: 'Opcja 2', consequence: 'Konsekwencja 2.', next_node_id: 'scena-6' },
      ],
    },
    {
      id: 'scena-6',
      type: 'decision',
      text: 'Scena 6 — ostatni wybór. Lorem ipsum dolor sit amet.',
      choices: [
        { id: 'c6-1', text: 'Opcja 1', consequence: 'Konsekwencja 1.', next_node_id: 'final-a' },
        { id: 'c6-2', text: 'Opcja 2', consequence: 'Konsekwencja 2.', next_node_id: 'final-b' },
      ],
    },
    {
      id: 'final-a',
      type: 'ending',
      title: 'Zakończenie A',
      text: 'Tekst zakończenia A. Lorem ipsum dolor sit amet.',
    },
    {
      id: 'final-b',
      type: 'ending',
      title: 'Zakończenie B',
      text: 'Tekst zakończenia B. Lorem ipsum dolor sit amet.',
    },
  ],
}
