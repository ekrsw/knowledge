import React from 'react';
import { Search, X, Filter } from 'lucide-react';
import { SearchFilters } from '../../types';
import { mockCategories, mockApprovalGroups } from '../../data/mockData';

interface SearchFiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onSearch: () => void;
}

export const SearchFiltersComponent: React.FC<SearchFiltersProps> = ({
  filters,
  onFiltersChange,
  onSearch,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const handleInputChange = (field: keyof SearchFilters, value: any) => {
    onFiltersChange({ ...filters, [field]: value });
  };

  const clearFilters = () => {
    onFiltersChange({
      keyword: '',
      articleNumber: '',
      importantOnly: false,
      category: '',
      approvalGroup: '',
      sortBy: 'articleNumber',
      sortOrder: 'asc',
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Search className="mr-2" size={20} />
            検索条件
          </h3>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="md:hidden p-2 text-gray-500 hover:text-gray-700 rounded-md"
          >
            <Filter size={20} />
          </button>
        </div>

        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                キーワード
              </label>
              <input
                type="text"
                value={filters.keyword}
                onChange={(e) => handleInputChange('keyword', e.target.value)}
                placeholder="FAQ内容を検索..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                記事番号
              </label>
              <input
                type="text"
                value={filters.articleNumber}
                onChange={(e) => handleInputChange('articleNumber', e.target.value)}
                placeholder="KBA-00000-00000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className={`space-y-4 ${isExpanded ? 'block' : 'hidden md:block'}`}>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="importantOnly"
                checked={filters.importantOnly}
                onChange={(e) => handleInputChange('importantOnly', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="importantOnly" className="ml-2 text-sm text-gray-700">
                重要のみ表示
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  情報カテゴリ
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">すべて</option>
                  {mockCategories.map((category) => (
                    <option key={category.id} value={category.name}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  承認グループ
                </label>
                <select
                  value={filters.approvalGroup}
                  onChange={(e) => handleInputChange('approvalGroup', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">すべて</option>
                  {mockApprovalGroups.map((group) => (
                    <option key={group.id} value={group.name}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  並び順
                </label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleInputChange('sortBy', e.target.value as any)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="articleNumber">記事番号順</option>
                  <option value="createdAt">投稿日順</option>
                  <option value="approvedAt">承認日順</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  順序
                </label>
                <select
                  value={filters.sortOrder}
                  onChange={(e) => handleInputChange('sortOrder', e.target.value as any)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="asc">昇順</option>
                  <option value="desc">降順</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <button
              onClick={onSearch}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center"
            >
              <Search className="mr-2" size={18} />
              検索実行
            </button>
            <button
              onClick={clearFilters}
              className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium flex items-center justify-center"
            >
              <X className="mr-2" size={18} />
              クリア
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};