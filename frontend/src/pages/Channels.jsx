import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getChannels, getCategories } from '../services/api'
import { Search, Filter } from 'lucide-react'

export default function Channels() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')

  const { data: channelsData, isLoading } = useQuery({
    queryKey: ['channels', { category }],
    queryFn: () => getChannels({ category: category || undefined }),
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  })

  const channels = channelsData?.data || []
  const categories = categoriesData?.data || []

  const filteredChannels = channels.filter(channel =>
    channel.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="px-4 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Channels</h1>

      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search channels..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div className="sm:w-64">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.name} value={cat.name}>
                {cat.name} ({cat.count})
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-10">Loading...</div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {filteredChannels.map((channel) => (
              <li key={channel.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center space-x-4">
                  {channel.logo_url && (
                    <img
                      src={channel.logo_url}
                      alt={channel.name}
                      className="h-12 w-12 object-contain"
                    />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-lg font-medium text-gray-900">{channel.name}</h3>
                      {channel.region && (
                        <span className="ml-2 px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                          {channel.region}
                        </span>
                      )}
                      {channel.variant && (
                        <span className="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                          {channel.variant}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 text-sm text-gray-500">
                      {channel.category} • {channel.stream_count} streams
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
