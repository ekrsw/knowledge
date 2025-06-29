import React, { useState, useMemo } from 'react';
import { Edit, Trash2, Eye, RefreshCw, Clock, CheckCircle, X, Filter } from 'lucide-react';
import { FAQ } from '../../types';
import { mockCategories } from '../../data/mockData';

interface MyPostsListProps {
  posts: FAQ[];
  onEdit: (faq: FAQ) => void;
  onDelete: (faq: FAQ) => void;
  onView: (faq: FAQ) => void;
  onResubmit: (faq: FAQ) => void;
}

export const MyPostsList: React.FC<MyPostsListProps> = ({
  posts,
  onEdit,
  onDelete,
  onView,
  onResubmit,
}) => {
  const [statusFilters, setStatusFilters] = useState({
    approved: true,
    pending: true,
    draft: true,
    rejected: true,
  });

  const filteredPosts = useMemo(() => {
    return posts.filter(post => {
      switch (post.status) {
        case 'approved':
          return statusFilters.approved;
        case 'pending':
          return statusFilters.pending;
        case 'draft':
          return statusFilters.draft;
        case 'rejected':
          return statusFilters.rejected;
        default:
          return true;
      }
    });
  }, [posts, statusFilters]);

  const handleFilterChange = (status: keyof typeof statusFilters) => {
    setStatusFilters(prev => ({
      ...prev,
      [status]: !prev[status]
    }));
  };

  const getCategoryColor = (categoryName: string) => {
    const category = mockCategories.find(c => c.name === categoryName);
    return category?.color || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status: FAQ['status']) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'pending':
        return <Clock className="text-yellow-500" size={16} />;
      case 'rejected':
        return <X className="text-red-500" size={16} />;
      case 'draft':
        return <Edit className="text-gray-500" size={16} />;
      default:
        return null;
    }
  };

  const getStatusText = (status: FAQ['status']) => {
    switch (status) {
      case 'approved':
        return '承認済み';
      case 'pending':
        return '承認待ち';
      case 'rejected':
        return '却下';
      case 'draft':
        return '下書き';
      default:
        return '';
    }
  };

  const getStatusCount = (status: FAQ['status']) => {
    return posts.filter(post => post.status === status).length;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Filter Section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center mb-4">
            <Filter className="mr-2" size={20} />
            ステータス絞り込み
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer">
              <input
                type="checkbox"
                checked={statusFilters.approved}
                onChange={() => handleFilterChange('approved')}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <div className="flex items-center space-x-2">
                <CheckCircle className="text-green-500" size={16} />
                <span className="text-sm font-medium text-gray-700">承認済み</span>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  {getStatusCount('approved')}
                </span>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer">
              <input
                type="checkbox"
                checked={statusFilters.pending}
                onChange={() => handleFilterChange('pending')}
                className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded"
              />
              <div className="flex items-center space-x-2">
                <Clock className="text-yellow-500" size={16} />
                <span className="text-sm font-medium text-gray-700">承認待ち</span>
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                  {getStatusCount('pending')}
                </span>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer">
              <input
                type="checkbox"
                checked={statusFilters.draft}
                onChange={() => handleFilterChange('draft')}
                className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
              />
              <div className="flex items-center space-x-2">
                <Edit className="text-gray-500" size={16} />
                <span className="text-sm font-medium text-gray-700">下書き</span>
                <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
                  {getStatusCount('draft')}
                </span>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer">
              <input
                type="checkbox"
                checked={statusFilters.rejected}
                onChange={() => handleFilterChange('rejected')}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <div className="flex items-center space-x-2">
                <X className="text-red-500" size={16} />
                <span className="text-sm font-medium text-gray-700">却下</span>
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                  {getStatusCount('rejected')}
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Posts List */}
      {filteredPosts.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl shadow-lg border border-gray-200">
          <div className="text-gray-400 mb-4">
            <Edit size={48} className="mx-auto" />
          </div>
          <p className="text-gray-500 text-lg">
            {posts.length === 0 ? '投稿したFAQはありません' : '選択した条件に該当する投稿はありません'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">マイ投稿一覧</h2>
            <p className="text-gray-600 mt-2">
              表示中: {filteredPosts.length}件 / 全{posts.length}件
            </p>
          </div>

          <div className="divide-y divide-gray-100">
            {filteredPosts.map((post) => (
              <div key={post.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(post.status)}
                      <span className="text-sm font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
                        {post.articleNumber}
                      </span>
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {getStatusText(post.status)}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(post.category)}`}>
                        {post.category}
                      </span>
                    </div>

                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {post.title}
                    </h4>

                    <div className="text-sm text-gray-600 space-y-1">
                      <div>投稿日: {formatDate(post.createdAt)}</div>
                      {post.approvedAt && (
                        <div>承認日: {formatDate(post.approvedAt)}</div>
                      )}
                      {post.rejectedAt && (
                        <div>却下日: {formatDate(post.rejectedAt)}</div>
                      )}
                      {post.rejectionReason && (
                        <div className="text-red-600">却下理由: {post.rejectionReason}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    {post.status === 'approved' && (
                      <button
                        onClick={() => onView(post)}
                        className="flex items-center bg-blue-100 text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                      >
                        <Eye className="mr-1" size={16} />
                        詳細表示
                      </button>
                    )}
                    
                    {(post.status === 'pending' || post.status === 'draft') && (
                      <>
                        <button
                          onClick={() => onEdit(post)}
                          className="flex items-center bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                        >
                          <Edit className="mr-1" size={16} />
                          編集
                        </button>
                        <button
                          onClick={() => onDelete(post)}
                          className="flex items-center bg-red-100 text-red-700 px-3 py-2 rounded-lg hover:bg-red-200 transition-colors text-sm"
                        >
                          <Trash2 className="mr-1" size={16} />
                          削除
                        </button>
                      </>
                    )}

                    {post.status === 'rejected' && (
                      <>
                        <button
                          onClick={() => onResubmit(post)}
                          className="flex items-center bg-green-100 text-green-700 px-3 py-2 rounded-lg hover:bg-green-200 transition-colors text-sm"
                        >
                          <RefreshCw className="mr-1" size={16} />
                          再投稿
                        </button>
                        <button
                          onClick={() => onDelete(post)}
                          className="flex items-center bg-red-100 text-red-700 px-3 py-2 rounded-lg hover:bg-red-200 transition-colors text-sm"
                        >
                          <Trash2 className="mr-1" size={16} />
                          削除
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};