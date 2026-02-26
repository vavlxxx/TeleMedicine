const MOCK_TESTIMONIALS = [
  {
    id: 't-101',
    rating: 5,
    quote:
      'За 20 минут получила консультацию терапевта и список анализов. Без очередей и поездки в клинику.',
    name: 'Марина В.',
    role: 'Самара',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuD4xLxbVzyGGTqC2Oiwc5UWtKlSklLAI7aRaGHOH__PorskryNocxAs30i_Bbcx4Bx7r13AaHu-QySXgzLmP-tDesJG26L-ak6N63PE2bqjPBGNyHojaPfp4FsooMeKddVNyQXweTMg8BHZtSL3ZSnWXoroNCh8vogA9l7wIFzBhDaQwSr830VcVEXCPca8LLrS3jtB6x6oAOZt4rd6c_Rs-edhLDBUoHY8t1OVIbYXJRyl9tR1rcE5RFb6JDHXEWDd9hCTuDRFFMLm',
  },
  {
    id: 't-102',
    rating: 5,
    quote:
      'Понравилось, что невролог подробно объяснил схему лечения и сразу отправил рекомендации в личный кабинет.',
    name: 'Алексей Д.',
    role: 'Казань',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuC-gnTlYjREOw0L0LoLhUaX5Yws8xGYepL_agjCrPKDR3xQjSuJ4jYuKEvWxpl7-LdUO1KSqODNP5WAPZrmERUnyDnOcTRywH7v5gODe2lvtjy2Og1sJweaV89rm5ig9clNPdvpadhwunOZ2g7Nv6vEadZhs1FyzBvKxzwkumU_Di8fefRCC4wB6bSmABGnSWz-fhlrh1YANTXwUx8m86jU3sJeq5caCEvVz6LqyL3pzS_9xZS89cAw3Woy2JYnWeolGgh0NYwC3JlN',
  },
  {
    id: 't-103',
    rating: 4,
    quote:
      'Обратилась ночью к педиатру: быстро подключились, успокоили и дали понятный план на ближайшие сутки.',
    name: 'Елена К.',
    role: 'Санкт-Петербург',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuCqhi_Kh_9vk0pD0OiEK_0vJ7WCAjcuZBsgAqSouJuHbeR5XwvpKzP9f6qxVjRV53ik-p7m0ci7qvCcOIaiAHsGpDkjVm-xKwk-vVgS_ugmq_5NfRYy3xVg57GgMi-Izu7jOb9xSHJVKFmhurzh9bQMdaf9PVKyVRBgYUEWvbtWfF7d2Bx15j5v-eroBM4fjpnnGfZt2CzatJ08YEGawkbvYJnqosQ6rxgnEOiN6tle1ze5Uk2SLAn15HUkz9tacyZYWB9CSDWI04Z7',
  },
  {
    id: 't-104',
    rating: 5,
    quote:
      'Удобно, что все выписки и назначения сохраняются в одном месте. Повторный прием занял буквально 15 минут.',
    name: 'Ирина П.',
    role: 'Екатеринбург',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDyTnpTESvu3uRVqoPZWnsbus0-8BTM7nmkbJ-JoBgcVU9NBLT1Qi0op55n2dEtTdwW4j_CkdKQIDYwlKqDAyzrg49-naQ5IlfNSCPyIGaPHwSQGU-t0MrWf4KTaYEjmsSLOffsD9BecAuwxvIrk4AHngQ9x_zuCkW6zbkiE02Nx1ajbr8NAhJ73Fs0MZdr2gjnc8WI7jDwQ6nL7kss7QipDJgGf9Nakm2XSK1ntQj1a43fE6tUHOIiYuAm76v3cGpCNm98iKaiwnEQ',
  },
]

export const fetchMockTestimonials = () =>
  new Promise((resolve) => {
    window.setTimeout(() => {
      resolve(MOCK_TESTIMONIALS)
    }, 480)
  })
